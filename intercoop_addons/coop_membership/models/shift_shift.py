# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import api, models, _


class ShiftShift(models.Model):
    _inherit = "shift.shift"

    @api.multi
    def button_done(self):
        '''
        Modify button done for
            - Create Point for FTOP shift on cloturing
                + Deduct 1 if current point > 1
                + Deduct 2 if current point < 1
        '''
        super(ShiftShift, self).button_done()
        point_counter_env = self.env['shift.counter.event']
        for shift in self:
            if shift.shift_type_id.is_ftop:
                for registration in shift.registration_ids:
                    partner = registration.partner_id
                    # Registration's state is waiting means the member is on
                    # vacation or exempted at the current shift. So, we don't
                    # deduct member's points
                    if registration.state == 'waiting':
                        continue
                    current_point = partner.final_ftop_point
                    point = 0
                    if current_point >= 1:
                        point = -1
                    else:
                        point = -2
                    # Create Point Counter
                    point_counter_env.sudo().with_context(
                        {'automatic': True}).create({
                            'name': _('Shift Cloture'),
                            'shift_id': shift.id,
                            'type': 'ftop',
                            'partner_id': partner.id,
                            'point_qty': point
                        })
