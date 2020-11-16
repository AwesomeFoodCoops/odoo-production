# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

rounding_limit = 0.00000000001
WEEK_LETTER = ['A', 'B', 'C', 'D']


class ReportWallchartCommon(models.AbstractModel):
    _name = 'report.coop_shift.report_wallchart_common'
    _description = 'Report Coop Shift Report Wallchart Common'

    def _get_number_weeks_per_cycle(self):
        get_param = self.env['ir.config_parameter'].sudo().get_param
        return int(get_param('coop_shift.number_of_weeks_per_cycle'))

    @api.model
    def _get_week_number(self, date):
        week_number = self.env['shift.template']._get_week_number(date)
        week_name = (
            week_number
            and self.env['shift.template']._number_to_letters(week_number)
        )
        return (week_number, week_name)

    @api.model
    def format_float_time(self, time):
        return '%s:%s' % (str(time).split('.')[0], int(float(str(
            '%.2f' % time).split('.')[1]) / 100 * 60) or "00")

    @api.model
    def _get_tickets(
            self, template,
            product_name='coop_shift.product_product_shift_standard'):
        return template.shift_ticket_ids.filtered(
            lambda t, s=self, p=product_name: t.product_id == s.env.ref(p))
