# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author Julien WESTE
# @author Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api, fields, _
from odoo.exceptions import ValidationError


class ShiftTemplateRegistration(models.Model):
    _inherit = 'shift.template.registration'

    partner_id = fields.Many2one(
        domain=[('is_worker_member', '=', True)])
    is_current_participant = fields.Boolean(
        compute="_compute_current_participant",
        search="_search_upper_current",
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
            reg.is_current_participant = \
                any(line.date_begin and line.date_begin <= today and
                    (not line.date_end or line.date_end >= today)
                    for line in reg.line_ids)

    def _search_upper_current(self, operator, value):
        domain = []
        today = fields.Date.context_today(self)
        template_id = self._context.get('active_id', False)
        if not template_id:
            return domain
        sql = """SELECT str.id
            FROM shift_template_registration_line strl
            JOIN shift_template_registration str
            ON strl.registration_id = str.id
            WHERE (strl.date_begin <= %s OR strl.date_begin is NULL)
            AND (strl.date_end >= %s
            OR strl.date_end is NULL) AND str.shift_template_id = %s
        """
        self.env.cr.execute(sql, (today, today, template_id))
        list_template_ids = self.env.cr.fetchall()
        list_ids = []
        for template_id in list_template_ids:
            list_ids.append(template_id[0])
        domain = [('id', 'in', list_ids)]
        return domain
