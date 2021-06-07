from odoo import api, models, _
from odoo.exceptions import UserError
from lxml import etree
from odoo.osv.orm import setup_modifiers


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.onchange("purchase_id")
    def purchase_order_change(self):
        if self.purchase_id:
            self.check_received_product(self.purchase_id)
        no_reference = False
        if not self.reference:
            no_reference = True
        res = super().purchase_order_change()
        if no_reference:
            self.reference = False
        for line in self.invoice_line_ids:
            suppliers = line.product_id.seller_ids.filtered(
                lambda x: x.name == self.partner_id
            )
            if suppliers:
                line.base_price = suppliers[0].base_price
        return res

    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu
        )

        # Read only field contact base specific groups
        account_advise = self.user_has_groups("account.group_account_manager")
        doc = etree.fromstring(res["arch"])
        if not account_advise:
            if view_type == "form":
                list_readonly_field = [
                    "journal_id",
                    "account_id",
                    "user_id",
                    "payment_term_id",
                    "fiscal_position_id",
                    "move_id",
                    "date",
                    "company_id",
                ]
                for node in doc.xpath("//field"):
                    if node.get("name") in list_readonly_field:
                        node.set("readonly", "1")
                        setup_modifiers(node)
            res["arch"] = etree.tostring(doc)

        return res

    @api.onchange("state", "partner_id", "invoice_line_ids")
    def _onchange_allowed_purchase_ids(self):
        result = super()._onchange_allowed_purchase_ids()
        if self.type == "in_refund":
            if result["domain"]["purchase_id"]:
                result["domain"]["purchase_id"][0] = (
                    "invoice_status",
                    "in",
                    ("to invoice", "invoiced"),
                )
        return result

    @api.model
    def create(self, vals):
        purchase_id_val = vals.get("purchase_id", False)
        if purchase_id_val:
            purchase_id = self.env["purchase.order"].browse(purchase_id_val)
            self.check_received_product(purchase_id)
        res = super().create(vals)
        return res

    @api.model
    def check_received_product(self, purchase_id):
        pickings = purchase_id.picking_ids
        have_not_receive_picking = any(
            picking.state not in ["done", "cancel"] for picking in pickings
        )
        if have_not_receive_picking:
            raise UserError(
                _("Please confirm reception before creating "
                  "an invoice for this PO")
            )

    def _prepare_invoice_line_from_po_line(self, line):
        data = super()._prepare_invoice_line_from_po_line(
            line
        )
        if self.type == "in_refund":
            qty_invoiced = 0.0
            for inv_line in line.invoice_lines:
                if inv_line.invoice_id.state not in ["cancel"]:
                    if (
                        inv_line.invoice_id.type == "in_invoice"
                        and inv_line.invoice_id.state == "paid"
                    ):
                        qty_invoiced += inv_line.uom_id._compute_quantity(
                            inv_line.quantity,
                            line.product_uom,
                        )
                    elif (
                        inv_line.invoice_id.type == "in_refund"
                        and inv_line.invoice_id.state == "paid"
                    ):
                        qty_invoiced -= inv_line.uom_id._compute_quantity(
                            inv_line.quantity,
                            line.product_uom,
                        )
            # get invoiced qty
            data.update({"quantity": qty_invoiced})
        return data

    @api.multi
    def button_update_prices(self):
        self.ensure_one()
        return self.env.ref("coop_purchase.supplier_info_update_act").read()[0]

    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        round_curr = self.currency_id.round
        for line in self.invoice_line_ids:
            if not line.account_id:
                continue
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            # discount computation
            # Rounding the price based on the partner discount computation
            # for supplier invoice or supplier refund
            if self.type in ['in_invoice', 'in_refund'] and \
                line.discount and \
                    self.partner_id.discount_computation == \
                    'unit_price':
                price_unit = round_curr(price_unit)

            if line.price_policy == 'package':
                quantity = line.product_qty_package
            else:
                quantity = line.quantity
            taxes = line.invoice_line_tax_ids.compute_all(
                price_unit, self.currency_id, quantity, line.product_id,
                self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(
                    tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                    tax_grouped[key]['base'] = round_curr(val['base'])
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += round_curr(val['base'])
        return tax_grouped
