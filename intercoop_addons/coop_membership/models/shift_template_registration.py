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

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class ShiftTemplateRegistration(models.Model):
    _inherit = 'shift.template.registration'

    partner_id = fields.Many2one(
        domain=[('is_worker_member', '=', True)])
    is_current_participant = fields.Boolean(
        compute="_compute_current_participant",
        search="search_upper_current",
        string="Current Participant")

    @api.multi
    @api.constrains('partner_id')
    def _check_partner_subscription(self):
        for reg in self:
            if not reg.partner_id.is_worker_member:
                raise ValidationError(_(
                    'This partner does not have a type A capital subscription!'
                ))

    @api.multi
    def _compute_current_participant(self):
        for reg in self:
            today = fields.Date.context_today(self)
            reg.is_current_participant =\
                any(line.date_begin <= today and
                    (not line.date_end or line.date_end >= today)
                    for line in reg.line_ids)

    def search_upper_current(self, operator, value):
        domain = []
        today = fields.Date.context_today(self)
        template_id = self._context.get('active_id', False)
        if not template_id:
            return domain
        sql = '''
            SELECT str.id
            FROM shift_template_registration_line strl
            JOIN shift_template_registration str
            ON strl.registration_id = str.id
            WHERE (strl.date_begin <= '%s') AND (strl.date_end >= '%s'
            OR  strl.date_end is NULL) AND str.shift_template_id = %s
        ''' % (today, today, template_id)
        self.env.cr.execute(sql)
        list_template_ids = self.env.cr.fetchall()
        list_ids = []
        for template_id in list_template_ids:
            list_ids.append(template_id[0])
        domain = [('id', 'in', list_ids)]
        return domain
