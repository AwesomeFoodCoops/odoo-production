# -*- coding: utf-8 -*-

from openerp import models, api


class ShiftRegistration(models.Model):
    _inherit = 'shift.registration'

    @api.model
    def get_coordinators(self):
        # Function return name of the coordinators with format:
        #   A, B, C, D
        coordinators = self.shift_id.user_ids and \
            self.shift_id.user_ids.mapped("name") or []
        if not coordinators:
            return ""
        return ", ".join(coordinators)
