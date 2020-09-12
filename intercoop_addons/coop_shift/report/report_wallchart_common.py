# -*- coding: utf-8 -*-
from openerp import api, models, fields, _
import datetime

rounding_limit = 0.00000000001


class ReportWallchartCommon(models.AbstractModel):
    _name = 'report.coop_shift.report_wallchart_common'

    @api.model
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

    @api.model
    def prerender_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        docargs = {
            '_': _,
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date': datetime.date,
        }
        return docargs

    @api.multi
    def render_html(self, data):
        docargs = self.prerender_html(data)
        return self.env['report'].render(
            'coop_shift.report_wallchart_common', docargs)
