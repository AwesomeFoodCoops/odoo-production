# -*- encoding: utf-8 -*-
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

from openerp import models, fields, api
from datetime import datetime, timedelta


class ReportTimesheet(models.TransientModel):
    _name = "report.timesheet"

    def _get_selected_shifts(self):
        shift_ids = self.env.context.get('active_ids', False)
        if shift_ids:
            return shift_ids

    @api.onchange('date_report')
    def _onchange_date_report(self):
        res = {}
        if self.date_report:
            date2 = datetime.strftime(
                datetime.strptime(self.date_report, '%Y-%m-%d') -
                timedelta(days=1), '%Y-%m-%d')
            res['domain'] = {'shift_ids': [
                '&', ('date_begin', '<=', self.date_report, ),
                ('date_end', '>', date2)]}
        else:
            res['domain'] = {'shift_ids': []}
        return res

    date_report = fields.Date(string="Date")
    shift_ids = fields.Many2many(
        'shift.shift', 'shift_timeshift_rel', 'timesheet_id', 'shift_id',
        string="Shifts", default=_get_selected_shifts)

    @api.multi
    def check_report(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_report', 'shift_ids'])[0]
        data['form']['used_context'] = dict(
            lang=self.env.context.get('lang', 'en_US'))
        return self.env['report'].get_action(
            self, 'coop_shift.report_timesheet', data=data)
