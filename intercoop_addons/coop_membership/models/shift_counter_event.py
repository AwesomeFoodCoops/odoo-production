# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, fields, models, _


class ShiftCounterEvent(models.Model):
    _inherit = 'shift.counter.event'

    holiday_id = fields.Many2one('shift.holiday', string="Holiday")
    sum_current_qty = fields.Integer(
        compute="compute_sum_current_qty",
        string="Sum",
        store=True)

    @api.multi
    @api.depends('point_qty', 'partner_id', 'type')
    def compute_sum_current_qty(self):
        for record in self:
            if record.partner_id and record.type == 'ftop':
                counter_event_before =\
                    record.partner_id.counter_event_ids.filtered(
                        lambda c: c.create_date < record.create_date
                        and c.type == 'ftop')
                record.sum_current_qty = record.point_qty
                for event in counter_event_before:
                    record.sum_current_qty += event.point_qty

    @api.multi
    def update_write_date(self):
        sql = '''
            UPDATE shift_counter_event
            SET write_date = create_date
            WHERE is_manual = false
        '''
        self.env.cr.execute(sql)
        return True
