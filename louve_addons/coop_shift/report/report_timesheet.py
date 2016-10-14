# -*- coding: utf-8 -*-

from openerp import api, models
import datetime
from datetime import date, timedelta


class ReportTimesheet(models.AbstractModel):
    _name = 'report.coop_shift.report_timesheet'

    @api.model
    def _get_shifts(self, date_report, shifts):
        if shifts:
            shifts = self.env['shift.shift'].browse(shifts)
        else:
            if not date_report:
                date_report = date.today()
            date2 = datetime.datetime.strftime(
                datetime.datetime.strptime(date_report, "%Y-%m-%d") +
                timedelta(days=1), "%Y-%m-%d")
            shifts = self.env['shift.shift'].search([
                '&', ('date_begin', '>=', date_report),
                ('date_begin', '<', date2)])

        result = []
        for shift in shifts:
            registrations = []
            ftops = []
            for reg in shift.registration_ids:
                if reg.shift_ticket_id.product_id == self.env.ref(
                        'coop_shift.product_product_shift_ftop'):
                    ftops.append(reg)
                else:
                    if reg.state != 'replacing':
                        registrations.append({
                            'registration': reg,
                            'replacement': reg.replacing_reg_id})
            result.append({
                'shift': shift,
                'registrations': registrations,
                'registration_number': len(registrations),
                'ftop': ftops,
                'ftop_number': len(ftops), })
        return result

    @api.multi
    def render_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        date_report = data['form'].get('date_report', date.today())
        shifts = data['form'].get('shift_ids', [])

        shifts_res = self.with_context(
            data['form'].get('used_context', {}))._get_shifts(
            date_report, shifts)
        docargs = {
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date': date,
            'Shifts': shifts_res,
        }
        return self.env['report'].render(
            'coop_shift.report_timesheet', docargs)
