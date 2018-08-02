# -*- coding: utf-8 -*-

from openerp import models, api
import pytz
from datetime import datetime


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model
    def get_time_by_user_lang(self, date, formats):
        # Function return an array by formats parameters:
        if not date or not formats:
            return False
        try:
            user_tz = self.tz or 'Europe/Paris'
            local = pytz.timezone(user_tz)
            date = pytz.utc.localize(datetime.strptime(
                date, "%Y-%m-%d %H:%M:%S")).astimezone(local)
            return [datetime.strftime(date, item) for item in formats]
        except:
            return False
