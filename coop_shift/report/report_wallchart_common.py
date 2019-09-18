# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields

rounding_limit = 0.00000000001
WEEK_LETTER = ['A', 'B', 'C', 'D']


class ReportWallchartCommon(models.AbstractModel):
    _name = 'report.coop_shift.report_wallchart_common'
    _description = 'Report Coop Shift Report Wallchart Common'

    @api.model
    def _get_week_number(self, test_date):
        if not test_date:
            return False
        weekA_date = fields.Date.from_string(
            self.env.ref('coop_shift.config_parameter_weekA').value)
        week_number = 1 + (((test_date - weekA_date).days // 7) % 4)
        return (week_number, WEEK_LETTER[week_number - 1])

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
