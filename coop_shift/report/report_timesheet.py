
import datetime
from datetime import date, timedelta

from odoo import api, models


class ReportTimesheet(models.AbstractModel):
    _name = 'report.coop_shift.report_timesheet'
    _description = 'Report Coop Shift Report Timesheet'

    @api.model
    def check_partner_on_leave(self, partner, tocheck_date):
        '''
        @Function to check if a partner is on leave on specific date
        Input:
            - partner: A partner record
            - tocheck_date: The date to check, expressed in string type under
            format 'yyyy-mm-dd'
        '''
        found_leave = self.env['shift.leave'].search_count(
            [('partner_id', '=', partner.id),
             ('state', '=', 'done'),
             ('start_date', '<=', tocheck_date),
             ('stop_date', '>=', tocheck_date)]
        )
        return found_leave > 0

    @api.model
    def _get_shifts(self, date_report, shifts):
        if shifts:
            shifts = self.env['shift.shift'].browse(shifts)
        else:
            if not date_report:
                date_report = date.today().strftime("%Y-%m-%d")
            date2 = datetime.datetime.strftime(
                datetime.datetime.strptime(date_report, "%Y-%m-%d") +
                timedelta(days=1), "%Y-%m-%d")
            shifts = self.env['shift.shift'].search([
                ('date_begin', '>=', date_report),
                ('date_begin', '<', date2),
                ('state', '!=', 'cancel')])

        result = []
        for shift in shifts:
            registrations = []
            ftops = []
            for reg in shift.registration_ids:
                if reg.state == 'cancel':
                    continue
                # Check if a partner is on leave on a report date
                is_on_leave = self.check_partner_on_leave(
                    reg.partner_id, date_report)

                if reg.shift_ticket_id.product_id == self.env.ref(
                        'coop_shift.product_product_shift_ftop'):
                    ftops.append([reg, is_on_leave])
                else:
                    if reg.state not in ('replacing', 'replaced') and reg.exchange_state != "in_progress":
                        registrations.append({
                            'registration': reg,
                            'is_on_leave': is_on_leave,
                            'replacement': reg.replacing_reg_id})
            result.append({
                'shift': shift,
                'registrations': registrations,
                'registration_number': len(registrations),
                'ftop': ftops,
                'ftop_number': len(ftops), })
        return result

    @api.model
    def _get_report_values(self, docids, data=None):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        date_report = data['form'].get(
            'date_report', date.today().strftime("%Y-%m-%d"))
        shifts = data['form'].get('shift_ids', [])
        shifts_res = self.with_context(
            data['form'].get(
                'used_context',
                {}))._get_shifts(
            date_report,
            shifts)
        return {
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date': date,
            'Shifts': shifts_res,
        }
