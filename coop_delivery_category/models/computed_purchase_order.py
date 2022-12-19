# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class ComputedPurchaseOrder(models.Model):
    _inherit = 'computed.purchase.order'

    delivery_categ_ids = fields.Many2many(
        comodel_name='delivery.category',
        string='Delivery Categories',
        relation="delivery_category_purchase",
        column1="pid",
        column2="cid",
    )

    @api.multi
    def get_psi_domain(self):
        args = super(ComputedPurchaseOrder, self).get_psi_domain()
        if self.delivery_categ_ids:
            template_ids = self.delivery_categ_ids.mapped("product_ids.id")
            args.append(("product_tmpl_id", "in", template_ids))
        return args

