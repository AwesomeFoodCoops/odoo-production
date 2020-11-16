# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models, api, _
from odoo.addons.queue_job.job import job

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
    _inherit = "pos.order"

    week_number = fields.Integer(
        string='Week Number',
        compute="_compute_week_number",
        store=True,
    )
    week_name = fields.Char(
        string='Week',
        compute="_compute_week_number",
        store=True,
    )
    week_day = fields.Char(
        string="Day",
        compute="_compute_week_number",
        store=True,
    )
    cycle = fields.Char(
        string="Cycle",
        compute="_compute_week_number",
        store=True,
    )
    search_year = fields.Char(
        string='Year (Search)',
        compute='_compute_date_search',
        multi='_date_search',
        store=True,
        index=True,
    )
    search_month = fields.Char(
        string='Month (Search)',
        compute='_compute_date_search',
        multi='_date_search',
        store=True,
        index=True,
    )
    search_day = fields.Char(
        string='Day (Search)',
        compute='_compute_date_search',
        multi='_date_search',
        store=True,
        index=True,
    )

    amount_total = fields.Float(store=True)

    @api.multi
    @api.depends("date_order")
    def _compute_week_number(self):
        number_to_letters = self.env['shift.template']._number_to_letters
        # Compute week numbers
        data = self.env['shift.template']._get_week_number_multi(
            records=self, field_name='date_order')
        for rec in self:
            if not rec.date_order:
                rec.update({
                    'week_number': False,
                    'week_name': False,
                    'week_day': False,
                    'cycle': False,
                })
            else:
                # Get week number
                week_number = data.get(rec.id)
                week_name = number_to_letters(week_number)
                # Compute week day
                week_day = _(
                    WEEK_DAY_MAP.get(
                        fields.Date.from_string(rec.date_order).weekday()
                    )
                )
                rec.update({
                    'week_number': week_number,
                    'week_name': week_name,
                    'week_day': week_day,
                    'cycle': "%s%s" % (week_name, week_day),
                })

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        lines_value_lst = order_fields.get("lines", [])
        updated_lines_lst = []
        for line_values in lines_value_lst:
            if line_values[-1].get("qty", 0):
                updated_lines_lst.append(line_values)
        order_fields["lines"] = updated_lines_lst
        return order_fields

    @api.multi
    @api.depends('date_order')
    def _compute_date_search(self):
        """ Merge from date_search_extended module from version 9
        remove date_search_extended module from version 12"""
        for rec in self:
            if rec.date_order:
                rec.search_year = rec.date_order.strftime('%Y')
                rec.search_month = rec.date_order.strftime('%Y-%m')
                rec.search_day = rec.date_order.strftime('%Y-%m-%d')
            else:
                rec.search_year = False
                rec.search_month = False
                rec.search_day = False

    @api.multi
    def _recompute_week_fields_async(self):
        NUM_RECORDS_PER_JOB = 1000
        chunked = [
            self[i: i + NUM_RECORDS_PER_JOB]
            for i in range(0, len(self), NUM_RECORDS_PER_JOB)
        ]
        # Create jobs
        for chunk in chunked:
            chunk.with_delay()._job_recompute_week_fields_async()
        return True

    @job
    def _job_recompute_week_fields_async(self):
        self._compute_week_number()
