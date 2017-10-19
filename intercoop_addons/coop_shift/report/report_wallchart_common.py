# -*- coding: utf-8 -*-
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

from openerp import api, models, fields, _
from datetime import date

rounding_limit = 0.00000000001
WEEK_LETTER = ['A', 'B', 'C', 'D']


class ReportWallchartCommon(models.AbstractModel):
    _name = 'report.coop_shift.report_wallchart_common'

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

    @api.model
    def prerender_html(self, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))

        docargs = {
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'date': date,
            '_': _,
        }
        return docargs

    @api.multi
    def render_html(self, data):
        docargs = self.prerender_html(data)
        return self.env['report'].render(
            'coop_shift.report_wallchart_common', docargs)
