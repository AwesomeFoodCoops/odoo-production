# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import fields, models, api, _
from datetime import datetime, timedelta
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class PosSession(models.Model):
    _inherit = 'pos.session'

    week_number = fields.Char(string='Week', compute="compute_week_number",
                              store=True)
    week_day = fields.Char(
        string="Day", compute="compute_week_day", store=True)
    cycle = fields.Char(string="Cycle", compute="compute_cycle", store=True)

    @api.multi
    @api.depends('start_at')
    def compute_week_number(self):
        for session in self:
            if not session.start_at:
                session.week_number = False
            else:
                weekA_date = fields.Date.from_string(
                    self.env.ref('coop_shift.config_parameter_weekA').value)
                start_at = fields.Date.from_string(session.start_at)
                week_number =\
                    1 + (((start_at - weekA_date).days // 7) % 4)
                if week_number == 1:
                    session.week_number = 'A'
                elif week_number == 2:
                    session.week_number = 'B'
                elif week_number == 3:
                    session.week_number = 'C'
                elif week_number == 4:
                    session.week_number = 'D'

    @api.multi
    @api.depends('start_at')
    def compute_week_day(self):
        for session in self:
            if session.start_at:
                start_at_object = datetime.strptime(
                    session.start_at, '%Y-%m-%d %H:%M:%S')
                wd = start_at_object.weekday()
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
    @api.depends('week_number', 'week_day')
    def compute_cycle(self):
        for session in self:
            session.cycle = "%s%s" % (session.week_number, session.week_day)

    # Custom Section
    @api.multi
    def update_cycle_pos_session(self):

        session_ids = self.ids
        num_session_per_job = 20
        splited_session_list = \
            [session_ids[i: i + num_session_per_job]
             for i in range(0, len(session_ids), num_session_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid,
                                   {'lang': 'fr_FR'})
        # Create jobs
        for session_list in splited_session_list:
            update_cycle_pos_session_job.delay(
                session, 'pos.session', session_list)
        return True


@job
def update_cycle_pos_session_job(session, model_name, session_list):
    ''' Job for compute cycle '''
    orders = session.env[model_name].with_context({'lang': 'fr_FR'}).browse(session_list)
    orders.compute_week_number()
    orders.compute_week_day()
    orders.compute_cycle()
