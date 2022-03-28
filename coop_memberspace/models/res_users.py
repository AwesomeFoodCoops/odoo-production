import calendar
import locale
import logging
from datetime import datetime, timedelta

import pytz
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = "res.users"

    public_active = fields.Boolean(
        "Public Active",
        help="Public your active status on website",
        default=False,
    )

    @api.model
    def get_time_by_user_lang(self, date, formats, obj=None, lang="fr_FR.utf8"):
        # Function return an array by formats parameters:
        if not obj:
            obj = {}
        if not date or not formats:
            return False
        try:
            locale.setlocale(locale.LC_TIME, str(lang))
        except Exception:
            _logger.debug("Can't set locale")

        try:
            user_tz = self.tz or self.env.user.tz or "Europe/Paris"
            local = pytz.timezone(user_tz)
            date = pytz.utc.localize(date).astimezone(local)
            rs = [
                datetime.strftime(date, item).capitalize()
                for item in formats
            ]
            if obj and obj.get("id", False):
                rs.append(obj["id"])
            return rs
        except Exception:
            _logger.debug("Error while convering time by user lang")
            return False

    @api.model
    def ftop_get_shift(self):
        user = self.env.user
        tmpl = user.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current
        )
        shift_env = self.env["shift.shift"]
        shifts_available = shift_env
        shifts = []
        if tmpl:
            shifts_available = (
                shift_env.sudo()
                .search(
                    [
                        ('state', '!=', 'cancel'),
                        (
                            "shift_template_id",
                            "!=",
                            tmpl[0].shift_template_id.id,
                        ),
                        (
                            "date_begin",
                            ">=",
                            (datetime.now() + timedelta(days=1)).strftime(
                                "%Y-%m-%d 00:00:00"
                            ),
                        ),
                    ]
                )
                .filtered(
                    lambda r, user=self.env.user: user.partner_id
                    not in r.registration_ids.mapped("partner_id")
                    and not r.shift_template_id.shift_type_id.is_ftop
                )
                .sorted(key=lambda r: r.date_begin)
            )
            for shift in shifts_available:
                tickets = shift.shift_ticket_ids.filtered(
                    lambda r: r.shift_type == "ftop"
                )
                seats_avail = sum(tickets.mapped("seats_available"))
                if seats_avail < 1:
                    continue
                if shift.seats_availability == 'limited' and \
                    shift.seats_reserved >= shift.seats_max:
                    continue
                shifts.append(
                    {
                        "id": shift.id,
                        "week_number": shift.week_number,
                        'week_name': shift.week_name,
                        "seats_avail": seats_avail,
                        "date_begin": user.get_time_by_user_lang(
                            shift.date_begin,
                            ["%A, %d %B", "%HH%M"],
                            lang=user.lang + ".utf8",
                        ),
                        "css_style": shift.css_color_style
                    }
                )
        return shifts

    @api.model
    def get_statistics_char(self):
        datas = []
        current_date = datetime.now()
        current_month = current_date.month
        for x in range(1, 13):
            if x > current_month:
                datas.append({"value": 0, "color": "transparent"})
                continue
            month_range = calendar.monthrange(current_date.year, x)
            first_day_of_month = current_date.replace(month=x, day=1).strftime(
                "%Y-%m-%d 00:00:00"
            )
            last_day_of_month = current_date.replace(
                month=x, day=month_range[1]
            ).strftime("%Y-%m-%d 23:59:59")
            value = 0
            pos_session = self.env['pos.session'].sudo().search(
                [
                    ('stop_at', '>=', first_day_of_month),
                    ('stop_at', '<=', last_day_of_month),
                    ('state', '=', 'closed')
                ]
            )
            if pos_session:
                value = sum(pos_session.mapped('order_ids.amount_total'))
            if x == current_month:
                datas.append({"value": value, "color": "#b2b7bb"})
                continue
            datas.append({"value": value, "color": "#efeb1d"})
        return datas
