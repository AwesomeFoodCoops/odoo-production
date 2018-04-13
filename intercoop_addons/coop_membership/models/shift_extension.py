# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models
from dateutil.relativedelta import relativedelta


class ShiftExtension(models.Model):
    _inherit = 'shift.extension'

    @api.onchange('type_id', 'partner_id', 'date_start')
    def onchange_type_id(self):
        '''
        @Function to suggest the end date for the member
        '''
        for extension in self:
            extension.date_stop = self.suggest_extension_date_stop(
                extension_type=extension.type_id,
                partner=extension.partner_id,
                date_start=extension.date_start)

    @api.model
    def suggest_extension_date_stop(self, extension_type, partner, date_start):
        '''
        @Function to suggest the date stop for the extensions
        '''
        date_stop = False
        if extension_type and date_start:
            if extension_type.extension_method == 'fixed_duration':
                date_start = fields.Date.from_string(date_start)
                date_stop = date_start +\
                    relativedelta(days=extension_type.duration)
            elif partner and extension_type.extension_method == \
                    'to_next_regular_shift':
                # Get next shift date
                _next_shift_time, next_shift_date = \
                    partner.get_next_shift_date()
                date_stop = next_shift_date
        return date_stop
