# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import fields, models, api, _


class PosOrder(models.Model):
    _inherit = "pos.order"

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

    @api.multi
    @api.depends("date_order")
    def compute_week_number(self):
        for order in self:
            if not order.date_order:
                order.week_number = False
            else:
                weekA_date = fields.Date.from_string(
                    self.env.ref("coop_shift.config_parameter_weekA").value
                )
                date_order = fields.Date.from_string(order.date_order)
                week_number = 1 + (((date_order - weekA_date).days // 7) % 4)
                if week_number == 1:
                    order.week_number = "A"
                elif week_number == 2:
                    order.week_number = "B"
                elif week_number == 3:
                    order.week_number = "C"
                elif week_number == 4:
                    order.week_number = "D"

    @api.multi
    @api.depends("date_order")
    def compute_week_day(self):
        for order in self:
            if order.date_order:
                wd = order.date_order.weekday()
                if wd == 0:
                    order.week_day = _("Mon")
                elif wd == 1:
                    order.week_day = _("Tue")
                elif wd == 2:
                    order.week_day = _("Wes")
                elif wd == 3:
                    order.week_day = _("Thu")
                elif wd == 4:
                    order.week_day = _("Fri")
                elif wd == 5:
                    order.week_day = _("Sat")
                elif wd == 6:
                    order.week_day = _("Sun")

    @api.multi
    @api.depends("week_number", "week_day")
    def compute_cycle(self):
        for order in self:
            order.cycle = "%s%s" % (order.week_number, order.week_day)

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
