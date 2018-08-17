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
        mail_template = self.env.ref("pos_receipt_by_email.email_send_pos_receipt")
        _logger.info("Start to send ticket")
        for order in self.search([('email_status', '=', 'to_send')]):
            mail_template.send_mail(order.id, force_send=True)
            order.email_status = 'sent'
            # Make sure we commit the change to not send ticket twice
            self.env.cr.commit()

    @api.multi
    def action_paid(self):
        res = super(PosOrder, self).action_paid()
        for order in self:
            if order.partner_id.email and order.partner_id.email_pos_receipt:
                order.email_status = 'to_send'
        return res

