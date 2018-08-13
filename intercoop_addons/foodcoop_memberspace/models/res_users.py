# -*- coding: utf-8 -*-

from openerp import models, api
import pytz
from datetime import datetime


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_time_by_user_lang(self, date, formats, obj={}):
        # Function return an array by formats parameters:
        if not date or not formats:
            return False
        try:
            user_tz = self.tz or self.env.user.tz or 'Europe/Paris'
            local = pytz.timezone(user_tz)
            date = pytz.utc.localize(datetime.strptime(
                date, "%Y-%m-%d %H:%M:%S")).astimezone(local)
            rs = [datetime.strftime(date, item) for item in formats]
            if obj and obj.get('id', False):
                rs.append(obj['id'])
            return rs
        except:
            return False

    @api.model
    def ftop_get_shift(self):
        user = self.env.user
        tmpl = user.partner_id.tmpl_reg_line_ids.filtered(
            lambda r: r.is_current)
        shift_env = self.env['shift.shift']
        shifts_available = shift_env
        if tmpl:
            shifts_available = shift_env.sudo().search([
                ('shift_template_id', '!=', tmpl[0].shift_template_id.id),
                ('date_begin', '>=', datetime.now().strftime(
                    '%Y-%m-%d 00:00:00')),
                ('state', '=', 'confirm')
            ]).filtered(lambda r, user=self.env.user:
                user.partner_id not in r.registration_ids.mapped('partner_id')
                ).sorted(key=lambda r: r.date_begin)
                    
        return shifts_available.read([])
