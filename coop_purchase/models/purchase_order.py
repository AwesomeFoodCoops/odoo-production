from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def button_update_prices(self):
        self.ensure_one()
        return self.env.ref("coop_purchase.supplier_info_update_act").read()[0]

    @api.multi
    def action_view_invoice(self):
        result = super(PurchaseOrder, self).action_view_invoice()
        if result.get('context') and \
                result['context'].get('default_reference'):
            del result['context']['default_reference']
        return result
