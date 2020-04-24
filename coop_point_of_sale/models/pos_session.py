# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models, api, _


class PosSession(models.Model):
    _inherit = "pos.session"

    week_number = fields.Char(
        string="Week", compute="compute_week_number", store=True
    )
    week_day = fields.Char(
        string="Day", compute="compute_week_day", store=True
    )
    cycle = fields.Char(string="Cycle", compute="compute_cycle", store=True)

    search_year = fields.Char(
        string='Year (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)

    search_month = fields.Char(
        string='Month (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)

    search_day = fields.Char(
        string='Day (Search)', compute='_compute_date_search',
        multi='_date_search', store=True, index=True)

    order_qty = fields.Integer(
        compute='_compute_orders', string='Orders Qty', store=True)

    amount_subtotal = fields.Monetary(
        compute='_compute_orders', string='Amount Subtotal', store=True)

    total_amount = fields.Monetary(
        compute='_compute_orders', string='Transactions Total', store=True)

    @api.multi
    @api.depends('order_ids.lines.price_subtotal_incl',
                 'order_ids.lines.price_subtotal')
    def _compute_orders(self):
        for session in self:
            session.order_qty = len(session.order_ids)
            session.total_amount = sum(
                session.mapped('order_ids.amount_total'))
            session.amount_subtotal = session.total_amount - sum(
                session.mapped('order_ids.amount_tax'))

    @api.multi
    @api.depends("start_at")
    def compute_week_number(self):
        for session in self:
            if not session.start_at:
                session.week_number = False
            else:
                weekA_date = fields.Date.from_string(
                    self.env.ref("coop_shift.config_parameter_weekA").value
                )
                start_at = fields.Date.from_string(session.start_at)
                week_number = 1 + (((start_at - weekA_date).days // 7) % 4)
                if week_number == 1:
                    session.week_number = "A"
                elif week_number == 2:
                    session.week_number = "B"
                elif week_number == 3:
                    session.week_number = "C"
                elif week_number == 4:
                    session.week_number = "D"

    @api.multi
    @api.depends("start_at")
    def compute_week_day(self):
        for session in self:
            if session.start_at:
                wd = session.start_at.weekday()
                if wd == 0:
                    session.week_day = _("Mon")
                elif wd == 1:
                    session.week_day = _("Tue")
                elif wd == 2:
                    session.week_day = _("Wes")
                elif wd == 3:
                    session.week_day = _("Thu")
                elif wd == 4:
                    session.week_day = _("Fri")
                elif wd == 5:
                    session.week_day = _("Sat")
                elif wd == 6:
                    session.week_day = _("Sun")

    @api.multi
    @api.depends("week_number", "week_day")
    def compute_cycle(self):
        for session in self:
            session.cycle = "%s%s" % (session.week_number, session.week_day)

    @api.multi
    @api.depends('start_at')
    def _compute_date_search(self):
        """ Merge from date_search_extended module from version 9
        remove date_search_extended module from version 12"""
        for rec in self:
            if rec.start_at:
                rec.search_year = rec.start_at.strftime('%Y')
                rec.search_month = rec.start_at.strftime('%Y-%m')
                rec.search_day = rec.start_at.strftime('%Y-%m-%d')
            else:
                rec.search_year = False
                rec.search_month = False
                rec.search_day = False
