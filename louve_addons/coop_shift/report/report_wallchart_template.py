# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
#    Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, models, fields, _
from datetime import timedelta, date, datetime

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

weekday_list = ["mo", "tu", "we", "th", "fr", "sa", "su", ]


class ReportWallchartTemplate(models.AbstractModel):
    _name = 'report.coop_shift.report_wallchart_template'
    _inherit = 'report.coop_shift.report_wallchart_common'

    @api.model
    def _get_ticket_partners(self, ticket):
        partners = []
        for reg in ticket.registration_ids:
            ok = False
            dates = ""
            for line in reg.line_ids:
                if (line.date_end and fields.Date.from_string(
                        line.date_end) <= date.today()) or\
                        line.state != "open":
                    continue
                ok = True
                if line.date_begin and fields.Date.from_string(
                        line.date_begin) > date.today():
                    date_begin = datetime.strftime(fields.Date.from_string(
                        line.date_begin) - timedelta(days=1), "%x")
                    dates = ("+ until %s " % date_begin) + dates
                if line.date_end:
                    date_end = datetime.strftime(fields.Date.from_string(
                        line.date_end) + timedelta(days=1), "%x")
                    dates = ("+ from %s " % date_end) + dates
            dates = dates and (" (" + dates[2:-1] + ")")
            if ok:
                partners.append({
                    'partner_id': reg.partner_id,
                    'dates': dates})
        return partners

    @api.model
    def _get_tickets(
            self, template,
            product_name='coop_shift.product_product_shift_standard'):
        product_name = 'coop_shift.product_product_shift_standard'
        return super(ReportWallchartTemplate, self)._get_tickets(
            template, product_name)

    @api.model
    def _get_template_info(self, template):
        tickets = self._get_tickets(template)
        partners = []
        seats_max = 0
        for ticket in tickets:
            partners += self._get_ticket_partners(ticket)
            seats_max += ticket.seats_max
        return partners, seats_max

    @api.model
    def _get_templates(self, data):
        final_result = []
        for week_day in data.keys():
            if week_day == "id" or not data.get(week_day, False):
                continue

            result = []
            sql = """SELECT start_time, end_time
                FROM shift_template
                WHERE %s is True
                GROUP BY start_time, end_time
                ORDER BY start_time""" % week_day
            self.env.cr.execute(sql)

            for t in self.env.cr.fetchall():
                res = {}
                res['start_time'] = self.format_float_time(t[0])
                res['end_time'] = self.format_float_time(t[1])
                base_search = [
                    ('start_time', '>=', t[0] - rounding_limit),
                    ('start_time', '<=', t[0] + rounding_limit),
                    ('end_time', '>=', t[1] - rounding_limit),
                    ('end_time', '<=', t[1] + rounding_limit),
                ]
                week_letter = ['A', 'B', 'C', 'D']
                for week in [1, 2, 3, 4]:
                    template = self.env['shift.template'].search(
                        base_search + [('week_number', '=', week)])
                    if not template:
                        res['partners' + week_letter[week - 1]] = []
                        res['free_seats' + week_letter[week - 1]] = 0
                        continue
                    template = template[0]
                    partners, seats_max = self._get_template_info(template)
                    res['partners' + week_letter[week - 1]] = partners
                    res['free_seats' + week_letter[week - 1]] =\
                        max(0, seats_max - len(partners))
                result.append(res)
            if result:
                final_result.append({
                    'day': WEEK_DAYS[week_day],
                    'next_dates': self._get_next_dates(
                        weekday_list.index(week_day)),
                    'times': result
                })
        return final_result

    @api.model
    def _get_next_dates(self, weekday):
        result = {}
        today = date.today()
        next_date = today + timedelta(days=(weekday - today.weekday()) % 7)
        week_number = self._get_week_number(next_date)
        for i in range(4):
            delta = (i + 1 - week_number[0]) % 4
            result["week" + ["A", "B", "C", "D"][i]] = "(%s, %s, ...)" % (
                datetime.strftime(
                    next_date + timedelta(weeks=delta), "%d/%m/%Y"),
                datetime.strftime(
                    next_date + timedelta(weeks=delta + 4), "%d/%m/%Y"),)
        return result

    @api.multi
    def render_html(self, data):
        docargs = self.prerender_html(data)
        docargs['Wallcharts'] = self._get_templates(data['form'])
        return self.env['report'].render(
            'coop_shift.report_wallchart_template', docargs)
