# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError

SUPPORTED_MODELS = [
    'account.invoice',
]

class InvoiceSupplierPriceUpdate(models.TransientModel):
    _name = 'invoice.supplier.price.update'

    show_discount = fields.Boolean()
    partner_id = fields.Many2one(comodel_name='res.partner')
    edi_line_ids = fields.One2many(
        comodel_name='supplier.info.update.line',
        inverse_name='inv_supplier_price_id'
    )
    edi_line2_ids = fields.One2many(
        comodel_name='supplier.info.update.line',
        inverse_name='inv_supplier_price_id'
    )

    @api.onchange('show_discount')
    def _onchange_show_discount(self):
        self.ensure_one()
        if self.show_discount:
            self.edi_line_ids = self.edi_line2_ids
            self.edi_line2_ids = self.env['supplier.info.update.line']
        else:
            self.edi_line2_ids = self.edi_line_ids
            self.edi_line_ids = self.env['supplier.info.update.line']

    @api.model
    def default_get(self, fields_list):
        res = super(InvoiceSupplierPriceUpdate, self).default_get(
            fields_list=fields_list)
        active_model = self._context.get('active_model', '')
        active_id = self._context.get('active_id', False)
        if active_model in SUPPORTED_MODELS and active_id:
            active_obj = self.env[active_model].browse(active_id)
            processed_lines = self.compute_process_lines(
                active_model, active_obj)
            show_discount = active_obj.partner_id.show_discount
            res.update({
                'edi_line_ids': processed_lines,
                'edi_line2_ids': processed_lines,
                'partner_id': active_obj.partner_id.id,
                'show_discount': show_discount,
            })
        return res

    @api.model
    def compute_process_lines(self, active_model, active_obj):
        """
        update product prices/order line prices based on latest EDI supplier prices (Only for EDI suppliers)
        :param active_model: Current active model
        :param active_obj: Current active object
        :return: computed lines
        """
        lines = []
        partner_id = active_obj.partner_id
        obj_lines = 'order_line' in active_obj and active_obj.order_line \
                    or active_obj.invoice_line_ids
        # For invoice date
        supplier_price_list_obj = self.env['supplier.price.list']
        price_date = active_model == 'account.invoice' \
            and active_obj.date_invoice or False
        # END
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
                if 'discount' in line:
                    line_discount = line.discount
                else:
                    seller_discount

                # Only for EDI suppliers
                if partner_id.is_edi:
                    product_code = selected_seller_id.product_code
                    price_domain = []
                    price_domain.append(('supplier_id', '=', partner_id.id))
                    price_domain.append(('supplier_code', '=', product_code))
                    if price_date:
                        price_domain.append(('apply_date', '<=', price_date))
                    edi_price = supplier_price_list_obj.search(price_domain, order="apply_date desc")
                    if edi_price:
                        line_price_unit = edi_price[0].price
                # End
                # Prepare values in current document line
                seller_values.update({
                    'price_unit': line_price_unit,
                    'discount': line_discount,
                })
                lines.append((0, 0, seller_values))
        return lines

    @api.multi
    def update_prices_second(self):
        self.ensure_one()
        active_model = self._context.get('active_model', '')
        active_id = self._context.get('active_id', False)
        active_obj = self.env[active_model].browse(active_id)
        lines = self.edi_line_ids.sorted()
        obj_lines_values = []
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
            if active_model == 'account.invoice':
                obj_lines_values.append((1, line.invoice_line_id.id, {'price_unit': updated_price_unit}))
        if active_model == 'account.invoice':
            active_obj.write({'invoice_line_ids': obj_lines_values})
        return True


class SupplierInfoUpdateLine(models.TransientModel):
    _inherit = 'supplier.info.update.line'

    inv_supplier_price_id = fields.Many2one(comodel_name='invoice.supplier.price.update')
