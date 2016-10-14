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

from openerp import models, fields, api, _
from openerp.exceptions import UserError


class ReportWallchart(models.TransientModel):
    _name = "report.wallchart"

    def _get_selected_shifts(self):
        shift_ids = self.env.context.get('active_ids', False)
        if shift_ids:
            return shift_ids

    @api.onchange('all_days')
    def _onchange_all_days(self):
        for f in ["mo", "tu", "we", "th", "fr", "sa", "su"]:
            self._fields[f].__set__(self, self.all_days)

    mo = fields.Boolean('Mon')
    tu = fields.Boolean('Tue')
    we = fields.Boolean('Wed')
    th = fields.Boolean('Thu')
    fr = fields.Boolean('Fri')
    sa = fields.Boolean('Sat')
    su = fields.Boolean('Sun')
    all_days = fields.Boolean('all')

    @api.multi
    def check_report(self, report):
        self.ensure_one()
        if not (self.mo or self.tu or self.we or self.th or self.fr or
                self.sa or self.su):
            raise UserError(_('You must check at least one day.'))
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read([
            "mo", "tu", "we", "th", "fr", "sa", "su"])[0]
        return self.env['report'].get_action(
            self, report, data=data)

    @api.multi
    def check_report_template(self):
        return self.check_report('coop_shift.report_wallchart_template')

    @api.multi
    def check_report_ftop(self):
        return self.check_report('coop_shift.report_wallchart_ftop')
