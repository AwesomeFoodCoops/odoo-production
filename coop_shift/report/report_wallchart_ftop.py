# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta, date
from odoo import api, models, fields, _
from .report_wallchart_common import rounding_limit

WEEK_DAYS = {
    'mo': _('Monday'),
    'tu': _('Tuesday'),
    'we': _('Wednesday'),
    'th': _('Thursday'),
    'fr': _('Friday'),
    'sa': _('Saturday'),
    'su': _('Sunday'),
}


class ReportWallchartFTOP(models.AbstractModel):
    _name = 'report.coop_shift.report_wallchart_ftop'
    _inherit = 'report.coop_shift.report_wallchart_common'

    @api.model
    def _get_weekday_number(self, wd):
        if wd == 'mo':
            return 0
        elif wd == 'tu':
            return 1
        elif wd == 'we':
            return 2
        elif wd == 'th':
            return 3
        elif wd == 'fr':
            return 4
        elif wd == 'sa':
            return 5
        elif wd == 'su':
            return 6
        else:
            return False

    @api.model
    def _get_tickets(
            self, shift, product_name='coop_shift.product_product_shift_ftop'):
        product_name = 'coop_shift.product_product_shift_ftop'
        return super(ReportWallchartFTOP, self)._get_tickets(
            shift, product_name)

    @api.model
    def _get_report_info(self, data):
        final_result = []
        n_weeks_cycle = self._get_number_weeks_per_cycle()
        for week_day in data.keys():
            if week_day == "id" or not data.get(week_day, False):
                continue

            header = []
            weekday_number = self._get_weekday_number(week_day)
            today_weekday_number = date.today().weekday()

            for week in range(1, n_weeks_cycle + 1):
                next_weekday_date = (
                    date.today()
                    + timedelta(
                        days=(weekday_number - today_weekday_number) % 7)
                    + timedelta(weeks=week)
                )
                week_number = self._get_week_number(next_weekday_date)
                header.append({
                    'date': next_weekday_date,
                    'date_string': fields.Date.to_string(next_weekday_date),
                    'week_number': week_number[0],
                    'week_letter': week_number[1],
                })

            dates = [
                datetime.strftime(h['date'], "\'%Y-%m-%d\'") for h in header]

            sql = """SELECT begin_time, end_time
                FROM shift_shift as ss, shift_type as st
                WHERE date_without_time IN %s AND ss.shift_type_id = st.id
                AND st.is_ftop = false
                GROUP BY begin_time, end_time
                ORDER BY begin_time
            """
            self.env.cr.execute(sql, (tuple(dates),))

            result = []
            for t in self.env.cr.fetchall():
                res = {}
                res['start_time'] = self.format_float_time(t[0])
                res['end_time'] = self.format_float_time(t[1])
                base_search = [
                    ('begin_time', '>=', t[0] - rounding_limit),
                    ('begin_time', '<=', t[0] + rounding_limit),
                    ('end_time', '>=', t[1] - rounding_limit),
                    ('end_time', '<=', t[1] + rounding_limit),
                    ('shift_type_id.is_ftop', '=', False),
                ]
                shift_list = []
                for h in header:
                    shift = self.env['shift.shift'].search(
                        base_search + [
                            ('date_without_time', '=', h['date_string'])])
                    if not shift:
                        shift_list.append({
                            'partners': [],
                            'free_seats': 0
                        })
                        continue
                    shift = shift[0]
                    partners, seats_max = self._get_shift_info(shift)
                    shift_list.append({
                        'partners': partners,
                        'free_seats': max(0, seats_max - len(partners))
                    })
                res['shift_list'] = shift_list
                result.append(res)
            final_result.append({
                'day': WEEK_DAYS[week_day],
                'times': result,
                'header': header
            })
        return final_result

    @api.model
    def _get_shift_info(self, shift):
        tickets = self._get_tickets(shift)
        partners = []
        seats_max = 0
        for ticket in tickets:
            partners += self._get_ticket_partners(ticket)
            seats_max += ticket.seats_max
        return partners, seats_max

    @api.model
    def _get_ticket_partners(self, ticket):
        partners = []
        for reg in ticket.registration_ids:
            partners.append(reg.partner_id)
        return partners

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        # docs = self.env[self.model].browse(self.env.context.get('active_id'))
        Wallcharts = self._get_report_info(data['form'])
        return {
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': model,
            'data': data['form'],
            'Wallcharts': Wallcharts,
            'docs': docs,
            'date': date,
        }
