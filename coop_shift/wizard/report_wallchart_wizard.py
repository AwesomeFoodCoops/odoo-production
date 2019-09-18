# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReportWallchart(models.TransientModel):
    _name = "report.wallchart"
    _description = "Report Wallchart"

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
    def check_report(self):
        self.ensure_one()
        if not (self.mo or self.tu or self.we or self.th or self.fr or
                self.sa or self.su):
            raise UserError(_('You must check at least one day.'))
        data = {}
        [data] = self.read()
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get(
            'active_model', 'report.wallchart')  # 'ir.ui.menu')
        data['form'] = self.read([
            "mo", "tu", "we", "th", "fr", "sa", "su"])[0]

        return data
        # return self.env['report'].get_action(
        #     self, report, data=data)

    @api.multi
    def check_report_template(self):
        return self.env.ref('coop_shift.wallchart_template').report_action(
            self, self.check_report())

    # @api.multi
    # def check_report_ftop(self):
    #     return self.check_report('coop_shift.report_wallchart_ftop')

    @api.multi
    def check_report_ftop(self):
        return self.env.ref('coop_shift.wallchart_ftop').report_action(
            self, self.check_report())
