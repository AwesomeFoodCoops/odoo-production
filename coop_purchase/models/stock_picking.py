from odoo import models, api, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def button_validate(self):
        for picking in self:
            for move_line in picking.move_line_ids:
                product = move_line.product_id
                if not product.available_in_pos:
                    raise UserError(
                        _('The product {} received should have '
                          '"available in pos"').format(product.name)
                    )
        return super().button_validate()
