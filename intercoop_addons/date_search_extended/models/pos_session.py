# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime
from openerp import models, fields, api
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class PosSession(models.Model):
    _inherit = 'pos.session'

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
    @api.depends('start_at')
    def _compute_date_search(self):
        date_scheme = '%Y-%m-%d %H:%M:%S'
        for item in self:
            if item.start_at:
                my_date = datetime.strptime(item.start_at, date_scheme)
                item.search_year = my_date.strftime('%Y')
                item.search_month = my_date.strftime('%Y-%m')
                item.search_day = my_date.strftime('%Y-%m-%d')
            else:
                item.search_year = False
                item.search_month = False
                item.search_day = False

    @api.multi
    def create_job_to_compute_date_search(self):
        pos_sessions = self.ids
        num_pos_session_per_job = 100
        splited_pos_session_list = \
            [pos_sessions[i: i + num_pos_session_per_job]
             for i in range(0, len(pos_sessions), num_pos_session_per_job)]
        # Prepare session for job
        session = ConnectorSession(self._cr, self._uid)
        # Create jobs
        for pos_session_list in splited_pos_session_list:
            compute_date_search_job.delay(
                session, 'pos.session', pos_session_list)
        return True


@job
def compute_date_search_job(session, model_name, session_list):
    """ Job for compute date_search of pos.session """
    pos_sessions = session.env[model_name].browse(session_list)
    pos_sessions._compute_date_search()

