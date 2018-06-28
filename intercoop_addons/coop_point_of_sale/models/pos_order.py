# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models, api, _
from datetime import datetime, timedelta
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class PosOrder(models.Model):
    _inherit = 'pos.order'

    week_number = fields.Char(string='Week', compute="compute_week_number",
                              store=True)
    week_day = fields.Char(
        string="Day", compute="compute_week_day", store=True)
    cycle = fields.Char(string="Cycle", compute="compute_cycle", store=True)

    @api.multi
    @api.depends('date_order')
    def compute_week_number(self):
        for order in self:
            if not order.date_order:
                order.week_number = False
            else:
                weekA_date = fields.Date.from_string(
                    self.env.ref('coop_shift.config_parameter_weekA').value)
                date_order = fields.Date.from_string(order.date_order)
                week_number =\
                    1 + (((date_order - weekA_date).days // 7) % 4)
                if week_number == 1:
                    order.week_number = 'A'
                elif week_number == 2:
                    order.week_number = 'B'
                elif week_number == 3:
                    order.week_number = 'C'
                elif week_number == 4:
                    order.week_number = 'D'

    @api.multi
    @api.depends('date_order')
    def compute_week_day(self):
        for order in self:
            if order.date_order:
                date_order_object = datetime.strptime(
                    order.date_order, '%Y-%m-%d %H:%M:%S')
                wd = date_order_object.weekday()
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
    @api.depends('week_number', 'week_day')
    def compute_cycle(self):
        for order in self:
            order.cycle = "%s%s" % (order.week_number, order.week_day)

    # Custom Section
    @api.multi
    def update_cycle_pos_order(self):

        order_ids = self.ids
        num_order_per_job = 20
        splited_order_list = \
            [order_ids[i: i + num_order_per_job]
             for i in range(0, len(order_ids), num_order_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   {'lang': 'fr_FR'})
        # Create jobs
        for order_list in splited_order_list:
            update_cycle_pos_order_job.delay(
                session, 'pos.order', order_list)
        return True


@job
def update_cycle_pos_order_job(session, model_name, order_list):
    ''' Job for compute cycle '''
    orders = session.env[model_name].with_context({'lang': 'fr_FR'}).browse(order_list)
    orders.compute_week_number()
    orders.compute_week_day()
    orders.compute_cycle()