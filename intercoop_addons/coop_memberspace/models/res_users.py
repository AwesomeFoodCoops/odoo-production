# -*- coding: utf-8 -*-

from openerp import api, fields, models
import pytz
from datetime import datetime, timedelta
import calendar
import locale
import logging
_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    public_active = fields.Boolean(
        "Public Active", help="Public your active status on website",
        default=False
    )

    @api.model
    def get_time_by_user_lang(self, date, formats, obj={}, lang='fr_FR.utf8'):
        # Function return an array by formats parameters:
        if not date or not formats:
            return False
        try:
            locale.setlocale(locale.LC_TIME, str(lang))
        except:
            _logger.debug("Can't set locale")

        try:
            user_tz = self.tz or self.env.user.tz or 'Europe/Paris'
            local = pytz.timezone(user_tz)
            date = pytz.utc.localize(datetime.strptime(
                date, "%Y-%m-%d %H:%M:%S")).astimezone(local)
            rs = [datetime.strftime(date, item).capitalize().decode('UTF-8') \
                for item in formats]
            if obj and obj.get('id', False):
                rs.append(obj['id'])
            return rs
        except:
            _logger.debug("Error while convering time by user lang")
            return False

    @api.model
    def ftop_get_shift(self):
        user = self.env.user
        tmpl = user.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current)
        shift_env = self.env['shift.shift']
        shifts_available = shift_env
        shifts = []
        if tmpl:
            shifts_available = shift_env.sudo().search([
                ('shift_template_id', '!=', tmpl[0].shift_template_id.id),
                ('date_begin', '>=', (
                    datetime.now() + timedelta(days=1)).strftime(
                        '%Y-%m-%d 00:00:00'))
            ]).filtered(lambda r, user=self.env.user:
                user.partner_id not in r.registration_ids.mapped('partner_id')
                and not r.shift_template_id.shift_type_id.is_ftop
            ).sorted(key=lambda r: r.date_begin)
            for shift in shifts_available:
                tickets = shift.shift_ticket_ids.filtered(
                    lambda r: r.shift_type == 'ftop')
                seats_avail = sum(tickets.mapped("seats_available"))
                if seats_avail < 1:
                    continue
                shifts.append({
                    'id': shift.id,
                    'week_number': shift.week_number,
                    'seats_avail': seats_avail,
                    'date_begin': user.get_time_by_user_lang(
                        shift.date_begin, ['%A, %d %B', '%HH%M'],
                        lang=user.lang + '.utf8')
                })
        return shifts

    @api.model
    def get_statistics_char(self):
        datas = []
        current_date = datetime.now()
        current_month = current_date.month
        for x in xrange(1, 13):
            if x > current_month:
                datas.append({'value': 0, 'color': 'transparent'})
                continue
            month_range = calendar.monthrange(current_date.year, x)
            first_day_of_month = current_date.replace(
                month=x, day=1).strftime("%Y-%m-%d 00:00:00")
            last_day_of_month = current_date.replace(
                month=x, day=month_range[1]).strftime("%Y-%m-%d 23:59:59")
            turnover_month = '''
                SELECT SUM(total_amount) / 1000
                FROM pos_session
                WHERE stop_at BETWEEN '%s' AND '%s'
                    AND state = 'closed'
            ''' % (first_day_of_month, last_day_of_month)
            self.env.cr.execute(turnover_month)
            value = self.env.cr.fetchone()[0] or 0
            if x == current_month:
                datas.append({'value': value, 'color': '#b2b7bb'})
                continue
            datas.append({'value': value, 'color': '#efeb1d'})
        return datas
