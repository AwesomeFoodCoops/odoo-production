# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class PickingEdi(models.Model):
    _name = "picking.edi"

    product_id = fields.Many2one(comodel_name="product.product")
    ordered_quantity = fields.Float()
    product_qty = fields.Float(string="EDI Quantity")
    package_qty = fields.Float(string="Product package")
    line_to_update_id = fields.Many2one(comodel_name="stock.pack.operation")
    picking_update_id = fields.Many2one(comodel_name="picking.update")


class PickingUpdate(models.Model):
    _name = "picking.update"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    done = fields.Boolean(readonly=True)
    name = fields.Many2one(
        comodel_name="stock.picking", string="Order picking", readonly=True
    )
    values_proposed_ids = fields.One2many(
        comodel_name="picking.edi",
        inverse_name="picking_update_id",
        string="Quantities to update",
        readonly=True,
    )

    @api.model
    def get_needaction_count(self):
        return len(self.search([("done", "=", False)]))

    @api.multi
    def button_update_picking_order(self):
        self.ensure_one()
        updated_quantities = []
        for proposition in self.values_proposed_ids:
            updated_quantities += [(1, proposition.line_to_update_id.id, {
                "product_qty_package": proposition.product_qty,
                "product_qty": proposition.product_qty *
                proposition.package_qty,
            },)]
        self.done = True
        self.name.write({"pack_operation_product_ids": updated_quantities})
        return True
