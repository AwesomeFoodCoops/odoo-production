from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    price_unit_tax = fields.Monetary(
        compute="_compute_price_unit_tax",
        string="Price Unit Tax Included",
        store=True,
    )
    price_discounted = fields.Monetary(
        compute="_compute_price_discounted",
        string="Discounted Price",
        store=True,
    )

    @api.multi
    @api.depends("price_total", "product_qty")
    def _compute_price_unit_tax(self):
        for pol in self:
            if pol.product_qty:
                pol.price_unit_tax = pol.price_total / pol.product_qty

    @api.multi
    @api.depends("price_unit", "discount")
    def _compute_price_discounted(self):
        for pol in self:
            pol.price_discounted = pol._get_discounted_price_unit()

    @api.multi
    def update_po_price_to_vendor_price(self):
        """
        @Function for the action of updating vendor price
        """
        update_main_vendor = self.env["ir.config_parameter"].sudo().get_param(
            "update_main_vendor_on_update_vendor_price", "False"
        )
        update_main_vendor = safe_eval(update_main_vendor)

        for po_line in self:
            product = po_line.product_id
            po_vendor = po_line.partner_id
            po_vendor_id = po_vendor.id
            po_product_unit_price = po_line.price_unit
            main_vendor = False

            # Find the appropriate vendor price
            vendor_price_line = product.seller_ids.filtered(
                lambda vp_line: vp_line.name.id == po_vendor_id
            )
            if vendor_price_line:
                if update_main_vendor:
                    min_sequence = (
                        min(product.seller_ids.mapped("sequence")) or 0
                    )
                    vendor_price_line = vendor_price_line[0]
                    current_sequence = vendor_price_line.sequence

                    # No update if the current vendor is the main one
                    if vendor_price_line.sequence != min_sequence:
                        for seller in product.seller_ids:
                            if (
                                seller.id != vendor_price_line.id
                                and seller.sequence < current_sequence
                            ):
                                seller.write({"sequence": seller.sequence + 1})
                        main_vendor = vendor_price_line.name
                        vendor_price_line.write({"sequence": min_sequence})

                # Update unit price
                vendor_price_line.write({"base_price": po_product_unit_price})

                # Reupdate the theoretical cost / base price
                product_template = product.product_tmpl_id
                product_template.auto_update_theoritical_cost_price()
                product_template.with_context(
                    selected_vendor=main_vendor
                )._compute_base_price()

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        prices = {}
        for line in self:
            if line.discount:
                prices[line.id] = line.price_unit
                line.price_unit *= (1 - line.discount / 100.0)

                # Rounding the Price Unit based on the Partner's Discount
                # computation
                partner_disc_computation = \
                    line.order_id.partner_id.discount_computation
                currency = line.order_id.currency_id
                if partner_disc_computation == 'unit_price':
                    line.price_unit = currency.round(line.price_unit)

            super(PurchaseOrderLine, line)._compute_amount()
            # restore prices
            if line.discount:
                line.price_unit = prices[line.id]
