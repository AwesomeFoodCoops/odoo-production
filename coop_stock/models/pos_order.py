from odoo import api, models
from odoo.addons.queue_job.job import job


class PosOrder(models.Model):
    _inherit = "pos.order"

    @api.multi
    def validate_wrong_pos_picking(self):
        self.ensure_one()
        for order in self:
            picking = order.picking_id
            to_delete_moves = picking.move_lines.filtered(
                lambda m: m.product_uom_qty == 0
            )
            to_delete_moves.unlink()
            picking.button_validate()

    @api.multi
    def create_job_to_validate_wrong_pos_picking(self):
        pos_orders = self.ids
        num_pos_order_per_job = 100
        splited_pos_order_list = [
            pos_orders[i: i + num_pos_order_per_job]
            for i in range(0, len(pos_orders), num_pos_order_per_job)
        ]
        # Prepare session for job
        # Create jobs
        for pos_order_list in splited_pos_order_list:
            self.with_delay().validate_picking_pos_order_session_job(
                pos_order_list
            )
        return True

    @job
    def validate_picking_pos_order_session_job(self, session_list):
        """ Job for validate wrong pos pickings """
        pos_orders = self.env['pos.order'].browse(session_list)
        pos_orders.validate_wrong_pos_picking()
