# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, fields, api, _
import logging
_logger = logging.getLogger(__name__)

class PosOrder(models.Model):

    _inherit = 'pos.order'

    email_status = fields.Selection([
        ('no_send', 'Do not Send'),
        ('to_send', 'To send'),
        ('sent', 'Sent')],
        default="no_send", string="Send Status")

    @api.model
    def _send_order_cron(self):
        mail_template = self.env.ref("email_pos_receipt.email_send_pos_receipt")
        _logger.info("Start to send ticket")
        for order in self.search([('email_status', '=', 'to_send')]):
            mail_template.send_mail(order.id, force_send=True)
            order.email_status = 'sent'
            # Make sure we commit the change to not send ticket twice
            self.env.cr.commit()

    @api.multi
    def action_paid(self):
        # Send e-receipt for the partner.
        # It depends on value of the field `receipt_option`
        # that we config in pos.config.settings
        #  receipt_option = 1: Don't send e-receipt
        #  receipt_option = 2 or 3: Send e-receipt

        res = super(PosOrder, self).action_paid()
        pos_config = self.env['pos.config.settings'].search(
            [], limit=1, order="id desc")
        receipt_options = pos_config and pos_config[0].receipt_options or False
        for order in self:
            if receipt_options in [2, 3] and order.partner_id.email:
                order.email_status = 'to_send'
        return res
