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
                    'price_unit': seller_price_unit,
                    'price_policy': seller_price_policy,
                    'discount': seller_discount,
                    'show_discount': partner_id.show_discount,
                    linked_line_key: line.id,
                    'seller_id': False,
                }
                line_price_unit = line.price_unit
                line_discount = 'discount' in line and line.discount \
                                or seller_discount

                line_price_unit = \
                    line_price_unit != seller_price_unit and \
                    line_price_unit or 0
                line_discount = \
                    line_discount != seller_discount and line_discount or 0

                # Prepare new line to update supplier info
                new_line_values = seller_values.copy()
                new_line_values.update({
                    'price_unit': line_price_unit,
                    'discount': line_discount,
                    'seller_id': selected_seller_id.id,
                })
                lines.append((0, 0, seller_values))
                lines.append((0, 0, new_line_values))
        return lines

    @api.multi
    def update_prices(self):
        self.ensure_one()
        lines = self.line_ids.sorted()
        for i in range(0, len(lines), 2):
            update_values = {}
            first_line = lines[i]
            second_line = lines[i+1]
            price_unit_1st = first_line.price_unit
            price_unit_2nd = second_line.price_unit
            if price_unit_2nd > 0 and price_unit_2nd != price_unit_1st:
                update_values['base_price'] = price_unit_2nd

            discount_1st = first_line.discount
            discount_2nd = second_line.discount
            if discount_2nd != discount_1st:
                update_values['discount'] = discount_2nd
            if update_values:
                seller_id = second_line.seller_id
                product_template = seller_id.product_tmpl_id

                seller_id.write(update_values)
                product_template.auto_update_theoritical_cost_price()
        return True
