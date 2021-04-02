# -*- coding: utf-8 -*-
from openerp import api, fields, models

supported_models = [
    'purchase.order',
    'account.invoice',
]


class SupplierInfoUpdate(models.TransientModel):
    _name = 'supplier.info.update'

    show_discount = fields.Boolean()
    partner_id = fields.Many2one(comodel_name='res.partner')
    line_ids = fields.One2many(
        comodel_name='supplier.info.update.line',
        inverse_name='update_id'
    )
    line2_ids = fields.One2many(
        comodel_name='supplier.info.update.line',
        inverse_name='update_id'
    )

    @api.onchange('show_discount')
    def _onchange_show_discount(self):
        self.ensure_one()
        if self.show_discount:
            self.line_ids = self.line2_ids
            self.line2_ids = self.env['supplier.info.update.line']
        else:
            self.line2_ids = self.line_ids
            self.line_ids = self.env['supplier.info.update.line']

    @api.model
    def default_get(self, fields_list):
        res = super(SupplierInfoUpdate, self).default_get(
            fields_list=fields_list)
        active_model = self._context.get('active_model', '')
        active_id = self._context.get('active_id', False)
        if active_model in supported_models and active_id:
            active_obj = self.env[active_model].browse(active_id)
            processed_lines = self.compute_process_lines(
                active_model, active_obj)
            show_discount = active_obj.partner_id.show_discount
            res.update({
                'line_ids': processed_lines,
                'line2_ids': processed_lines,
                'partner_id': active_obj.partner_id.id,
                'show_discount': show_discount,
            })
        return res

    @api.model
    def compute_process_lines(self, active_model, active_obj):
        """
        Compute lines to process update prices action
        :param active_model: Current active model
        :param active_obj: Current active object
        :return: lines
        """
        lines = []
        partner_id = active_obj.partner_id
        obj_lines = 'order_line' in active_obj and active_obj.order_line \
                    or active_obj.invoice_line_ids
        for line in obj_lines:
            product_id = line.product_id
            selected_seller_id = product_id.seller_ids.filtered(
                lambda seller: seller.name == partner_id
                               and seller.price_policy == line.price_policy)
            selected_seller_id = \
                selected_seller_id and selected_seller_id[0] or False
            if selected_seller_id:
                seller_price_unit = selected_seller_id.base_price
                seller_discount = selected_seller_id.discount
                seller_price_policy = selected_seller_id.price_policy
                linked_line_key = \
                    active_model == 'purchase.order' and 'po_line_id' \
                    or 'invoice_line_id'
                seller_values = {
                    'product_id': product_id.id,
                    'price_policy': seller_price_policy,
                    'supplier_price_unit': seller_price_unit,
                    'supplier_discount': seller_discount,
                    'show_discount': partner_id.show_discount,
                    linked_line_key: line.id,
                    'seller_id': selected_seller_id.id,
                }

                line_price_unit = line.price_unit
                line_discount = 'discount' in line and line.discount \
                                or seller_discount

                # Prepare values in current document line
                seller_values.update({
                    'price_unit': line_price_unit,
                    'discount': line_discount,
                })
                lines.append((0, 0, seller_values))
        return lines

    @api.multi
    def update_prices(self):
        self.ensure_one()
        lines = self.line_ids.sorted()
        for line in lines:
            update_values = {}
            supplier_price_unit = line.supplier_price_unit
            updated_price_unit = line.price_unit
            if updated_price_unit > 0 and updated_price_unit != supplier_price_unit:
                update_values['base_price'] = updated_price_unit

            supplier_discount = line.supplier_discount
            updated_discount = line.discount
            if updated_discount != supplier_discount:
                update_values['discount'] = updated_discount
            if update_values:
                seller_id = line.seller_id
                product_template = seller_id.product_tmpl_id

                seller_id.write(update_values)
                product_template.auto_update_theoritical_cost_price()
        return True
