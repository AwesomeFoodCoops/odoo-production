
import datetime
from odoo import fields, models, api, _
import odoo.addons.decimal_precision as dp
from odoo.exceptions import UserError


class StockInventory(models.Model):
    _inherit = "stock.inventory"

    exhausted = fields.Boolean(default=True)

    @api.depends('date')
    def _get_week_number(self):
        for inventory in self:
            if not inventory.date:
                inventory.week_number = 0
            else:
                week_number = datetime.datetime.strptime(
                    str(inventory.date), "%Y-%m-%d %H:%M:%S").strftime("%W")
                inventory.week_number = week_number

    week_number = fields.Integer(string="Week Number",
                                 compute="_get_week_number",
                                 store=True,
                                 help="Number of Inventory Week")
    week_date = fields.Date(
        string="Began order scheduling on.", help="Week planning start date")
    hide_initialisation = fields.Boolean(
        string="Hide initialisation area", help="Hide Init. area",
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    categ_ids = fields.Many2many(
        'product.category', 'stock_inventory_product_categ', 'inventory_id',
        'categ_id', string='Product categories',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    supplier_ids = fields.Many2many(
        'res.partner', 'stock_inventory_res_partner', 'inventory_id',
        'supplier_id', string='Suppliers',
        domain=[('supplier', '=', True), ('is_company', '=', True)],
        help="Specify product category to focus in your inventory.",
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    weekly_inventory = fields.Boolean(
        string="Is a weekly inventory",
        help="Technical field to distinct odoo inventory with weekkly inventory ",
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.model
    def _get_planning_line_from_inv_line(self, inv_lines):
        line_vals = []
        for line in inv_lines:
            supplier_info = line.product_id.seller_ids and \
                line.product_id.seller_ids[0] or False
            val = {
                'product_id': line.product_id.id,
                'supplier_id': supplier_info and
                supplier_info.name.id or False,
                # set to this value because this value is used on purchase
                # order
                'price_unit': supplier_info and \
                supplier_info.base_price or 0.0,
                # set to this value because this value is used on purchase
                # order
                'price_policy': supplier_info and \
                supplier_info.price_policy or 'uom',
                'default_packaging': line.product_id.default_packaging,
                'supplier_packaging': supplier_info and \
                supplier_info.package_qty or 0,
                # it should be this. To be vaildated by coop :
                # line.packaging_qty *
                # line.product_id.default_packaging/(supplier_info.package_qty
                # or 1),
                'start_inv': line.qty_stock
            }
            line_vals.append(val)
        return line_vals

    @api.multi
    def action_generate_planification(self):
        """ Generate the Planification
        """
        self.ensure_one()
        line_vals = self._get_planning_line_from_inv_line(self.line_ids)
        week_planning_obj = self.env['order.week.planning']

        week_planning_value = {
            'date': self.week_date,
            'line_ids': [(0, 0, x) for x in line_vals],
            'hide_initialisation': True
        }
        new_id = week_planning_obj.create(week_planning_value)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'order.week.planning',
            'res_id': new_id.id,
            'view_mode': 'form',
            'target': 'current',
        }

    @api.multi
    def action_done(self):
        check_date_begin = self._context.get('check_date_begin', False)
        for stock_inventory in self:
            if not stock_inventory.week_date and check_date_begin:
                return {
                    'type': 'ir.actions.act_window',
                    'res_model': 'stock.inventory.wizard',
                    'res_id': False,
                    'view_mode': 'form',
                    'target': 'new',
                }
        return super(StockInventory, self).action_validate()

    def _coop_produce_get_inventory_lines(self):
        '''
            Function inspired from stock/stock.py to add categories filters
            and adds categ_ids, suppliers to the filter
        '''
        location_obj = self.env['stock.location']
        product_obj = self.env['product.product']
        supplierinfo_obj = self.env['product.supplierinfo']
        location_ids = location_obj.search(
            [('id', 'child_of', self.location_id.ids)])
        domain = ' sq.location_id in %s'
        vals = []
        product_ids = []
        args = (tuple(location_ids.ids),)
        if self.company_id.id:
            domain += ' and sq.company_id = %s'
            args += (self.company_id.id,)

        # Look for already existing product
        already_added_product_ids = self.line_ids.mapped('product_id')

        if self.categ_ids:
            # Look for products belong to selectec categories
            product_ids = product_obj.search(
                [('categ_id', 'in', self.categ_ids.ids)]).ids

        if self.supplier_ids:
            # Look for products belong to selectecd categories
            supplierinfo_ids = supplierinfo_obj.search(
                [('name', 'in', self.supplier_ids.ids)])

            product_tmpl_ids = supplierinfo_ids.mapped('product_tmpl_id')

            product_ids += product_obj.search(
                [('product_tmpl_id', 'in', product_tmpl_ids.ids)]).ids

        # treate only new poducts to add and no modification to existing
        # products
        product_ids = set(product_ids) ^ set(already_added_product_ids.ids)
        if not product_ids:
            return vals
        else:
            domain += ' and product_id in %s'
            args += (tuple(list(product_ids)),)
        query = '''
           SELECT sq.product_id as product_id,
                    pt.default_packaging as default_packaging,
                    pt.uom_id as product_uom_id,
                    sum(sq.quantity) as product_qty,
                    COALESCE(sum(sq.quantity)/pt.default_packaging,1.0)
                    as packaging_qty,
                    sq.location_id as location_id
           FROM stock_quant sq
           INNER JOIN product_product pp ON ( sq.product_id = pp.id)
           INNER JOIN product_template pt ON ( pp.product_tmpl_id = pt.id)
           WHERE''' + domain + '''
           GROUP BY sq.product_id, pt.default_packaging, pt.uom_id,
           sq.location_id
        '''
        self._cr.execute(query, args)

        found_product_ids = []
        for product_line in self._cr.dictfetchall():
            product_line['inventory_id'] = self.id
            # Reset quantity to force the user to set the quantity manually
            product_line['product_qty'] = 0.0
            vals.append(product_line)
            found_product_ids.append(product_line['product_id'])

        unfound_product_ids = list(set(product_ids) - set(found_product_ids))
        for product in product_obj.browse(unfound_product_ids):
            vals.append({
                'product_id': product.id,
                'default_packaging': product.default_packaging,
                'product_uom_id': product.uom_id.id,
                'packaging_qty': 0.0,
                'product_qty': 0.0,
                'location_id': self.location_id.id,
                'inventory_id': self.id,
            })

        return vals

    def action_add_category_supplier(self):
        if len(self.ids) > 1:
            raise UserError(_("You should on one inventory in the same time"))

        lines = self._coop_produce_get_inventory_lines()
        self.line_ids.create(lines)
        return True

    @api.multi
    def action_reset(self):
        for inventory in self:
            inventory.line_ids.unlink()
        return True

    @api.multi
    def init_with_theorical_qty(self):
        for inventory in self:
            for line in inventory.line_ids:
                line.write(
                    {'product_qty': (
                        line.packaging_qty * line.default_packaging),
                     'stock_qty': line.packaging_qty})


class StockInventoryLine(models.Model):
    _inherit = "stock.inventory.line"

    def _get_qty_loss(self):
        for line in self:
            line.qty_loss = (line.qty_stock - line.packaging_qty) or 0.00

    default_packaging = fields.Float(
        string='Default packaging', readonly=True)
    packaging_qty = fields.Float(
        string='Theorical packaging qty', readonly=True,
        digits=dp.get_precision('Product Unit of Measure'))
    qty_loss = fields.Float(
        compute='_get_qty_loss', string='Quantity Lost',
        digits=dp.get_precision('Product Unit of Measure'),
        help='Quantity Theoric Of Reference - Stock Quantity')
    qty_stock = fields.Float(string='Stock Quantity', digits=dp.get_precision(
        'Product Unit of Measure'), help="Stock Quantity")

    @api.onchange('qty_stock')
    def onchange_qty_stock(self):
        if not self.product_id:
            return self.onchange_product_id()
        if not self.default_packaging:
            return {'warning': {
                'title': _('Warning: wrong default packaging'),
                'message': _(
                    'The default packaging is not defined on the product')}
                    }
        else:
            return {'value': {
                    'qty_loss': self.qty_stock - self.packaging_qty,
                    'product_qty': self.qty_stock * self.default_packaging}
                    }

    @api.onchange('product_id')
    def onchange_product_id(self):
        if not self.product_id:
            return {'value': {'default_packaging': False,
                              'packaging_qty': False,
                              'qty_loss': False,
                              'product_qty': 0.0,
                              }}
        default_packaging = self.product_id.default_packaging
        if default_packaging:
            packaging_qty = self.product_id.qty_available / default_packaging
            ret = {'value': {'default_packaging': default_packaging,
                             'packaging_qty': packaging_qty,
                             'qty_stock': 0.0,
                             'qty_loss': -packaging_qty,
                             'product_qty': 0.0
                             }}
        else:
            ret = {'value': {'default_packaging': 0.0,
                             'packaging_qty': 0.0,
                             'qty_stock': 0.0,
                             'qty_loss': 0.0,
                             'product_qty': 0.0
                             }}
            ret['warning'] = {
                'title': _('Warning: wrong default packaging'),
                'message': _(
                    'The default packaging is not defined on the product')}
        return ret
