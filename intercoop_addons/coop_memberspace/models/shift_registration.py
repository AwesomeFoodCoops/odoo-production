# -*- coding: utf-8 -*-

from openerp import models, api


class ShiftRegistration(models.Model):
    _inherit = 'shift.registration'

    @api.model
    def get_coordinators(self, shift_regis_id=None):
        # Function return name of the coordinators with format:
        #   A, B, C, D

        # @param shift_id: Use to call function in js.
        shift = shift_regis_id and self.browse(shift_regis_id) and \
            self.browse(shift_regis_id).shift_id or self.shift_id
        coordinators = shift.user_ids and \
            shift.user_ids.mapped("name") or []
        if not coordinators:
            return ""
        return ", ".join(coordinators)
