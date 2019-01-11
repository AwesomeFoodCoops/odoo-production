# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Use exempted_member_status of leave to recompute member state

    @api.depends(
        'is_blocked', 'final_standard_point',
        'final_ftop_point', 'shift_type', 'date_alert_stop',
        'date_delay_stop', 'leave_ids.state',
        'leave_ids.forced_member_status')
    @api.multi
    def _compute_working_state(self):
        """Override method from coop_shift for parental leave improvement"""
        current_datetime = fields.Datetime.now()
        today = fields.Date.today()
        for partner in self:
            state = 'up_to_date'
            if partner.is_blocked:
                state = 'blocked'
            elif partner.is_vacation:
                state = 'vacation'
            else:
                if partner.in_ftop_team:
                    point = partner.final_ftop_point
                else:
                    point = partner.final_standard_point

                if point < 0:
                    if partner.date_alert_stop:
                        if partner.date_delay_stop > current_datetime:
                            # There is Delay
                            state = 'delay'
                        elif partner.date_alert_stop > current_datetime:
                            # Grace State
                            state = 'alert'
                        else:
                            state = 'suspended'
                    else:
                        state = 'suspended'
                elif partner.is_exempted:
                    state = 'exempted'
            # Change the status from Up to Date
            # to Alert if standard_counter < 0
            if state == 'up_to_date' and partner.final_standard_point < 0:
                state = 'alert'

            # Check member force status in shift.leave
            parental_leaves = partner.leave_ids.filtered(
                lambda l: l.is_parental_leave
                and l.start_date <= today <= l.stop_date
                and l.forced_member_status
            )
            # If member has one parental_leave and does not provide birthday
            #  certificate set member status to exempted
            if parental_leaves and parental_leaves[0]:
                state = parental_leaves[0].forced_member_status

            if partner.working_state != state:
                partner.working_state = state
