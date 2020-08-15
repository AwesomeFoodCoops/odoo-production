# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models, api, _
from datetime import datetime, timedelta
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

WEEK_DAY_MAP = {
    0: "Mon",
    1: "Tue",
    2: "Wes",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}


class PosOrder(models.Model):
    _inherit = 'pos.order'

    week_number = fields.Integer(
        string='Week Number',
        compute="_compute_week_number",
        store=True,
    )
    week_name = fields.Char(
        string='Week',
        compute="_compute_week_name",
        store=True,
    )
    week_day = fields.Char(
        string="Day",
        compute="_compute_week_day",
        store=True,
    )
    cycle = fields.Char(
        string="Cycle",
        compute="_compute_cycle",
        store=True,
    )

    @api.multi
    @api.depends('date_order')
    def _compute_week_number(self):
        for rec in self:
            rec.week_number = self.env['shift.template']._get_week_number(
                fields.Date.from_string(rec.date_order))

    @api.multi
    @api.depends('week_number')
    def _compute_week_name(self):
        for rec in self:
            if rec.week_number:
                rec.week_name = self.env['shift.template']._number_to_letters(
                    rec.week_number)
            else:
                rec.week_name = False

    @api.multi
    @api.depends('date_order')
    def _compute_week_day(self):
        for rec in self:
            if rec.date_order:
                wd = fields.Date.from_string(rec.date_order).weekday()
                rec.week_day = _(WEEK_DAY_MAP.get(wd))

    @api.multi
    @api.depends('week_name', 'week_day')
    def _compute_cycle(self):
        for rec in self:
            rec.cycle = "%s%s" % (rec.week_name, rec.week_day)

    # Custom Section

    def _order_fields(self, cr, uid, ui_order, context=None):
        res = super(PosOrder, self)._order_fields(cr, uid, ui_order, context)
        lines_value_lst = res.get('lines', [])
        updated_lines_lst = []
        for line_values in lines_value_lst:
            if line_values[-1].get('qty', 0):
                updated_lines_lst.append(line_values)
        res['lines'] = updated_lines_lst
        return res

    @api.multi
    def _recompute_week_fields_async(self):
        NUM_RECORDS_PER_JOB = 200
        record_ids = self.ids
        chunked = [
            record_ids[i: i + NUM_RECORDS_PER_JOB]
            for i in range(0, len(record_ids), NUM_RECORDS_PER_JOB)
        ]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid, {'lang': 'fr_FR'})
        # Create jobs
        for chunk in chunked:
            _job_recompute_week_fields_async.delay(session, chunk)
        return True

    @api.multi
    def _recompute_week_fields(self):
        self._compute_week_number()
        self._compute_week_name()
        self._compute_week_day()
        self._compute_cycle()


@job
def _job_recompute_week_fields_async(session, record_ids):
    ''' Job for compute cycle '''
    records = session.env['pos.order'].with_context(
        lang='fr_FR').browse(record_ids)
    records._recompute_week_fields()
