# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models


class ShiftRegistration(models.Model):
    _inherit = "shift.registration"

    @api.multi
    def button_reg_absent(self):
        email_template = "louve_custom_email.louve_unsubscribe_email"
        return super(
            ShiftRegistration, self.with_context(
                unsubscribe_email_template=email_template)).button_reg_absent()
