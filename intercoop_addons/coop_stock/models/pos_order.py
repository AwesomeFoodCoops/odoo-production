# -*- coding: utf-8 -*-

from openerp import api, models
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession



class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.multi
    def validate_wrong_pos_picking(self):
        for order in self:
            picking = order.picking_id
            to_delete_moves = picking.move_lines_related.filtered(
                lambda m: m.product_uom_qty == 0)
            to_delete_moves.unlink()
            picking.do_new_transfer()

    @api.multi
    def create_job_to_validate_wrong_pos_picking(self):
        pos_orders = self.ids
        num_pos_order_per_job = 100
        splited_pos_order_list = \
            [pos_orders[i: i + num_pos_order_per_job]
             for i in range(0, len(pos_orders), num_pos_order_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid)
        # Create jobs
        for pos_order_list in splited_pos_order_list:
            validate_picking_pos_order_session_job.delay(
                session, 'pos.order', pos_order_list)
        return True


@job
def validate_picking_pos_order_session_job(
        session, model_name, session_list):
    """ Job for validate wrong pos pickings """
    pos_orders = session.env[model_name].browse(session_list)
    pos_orders.validate_wrong_pos_picking()

