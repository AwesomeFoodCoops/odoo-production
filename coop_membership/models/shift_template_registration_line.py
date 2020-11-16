# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ShiftTemplateRegistrationLine(models.Model):
    _inherit = 'shift.template.registration.line'

    @api.multi
    def update_partner_shift_type(self):
        for record in self:
            ticket_shift_type = \
                record.registration_id.shift_ticket_id.shift_type
            partner = record.registration_id.partner_id
            partner_shift_type = partner.shift_type

            # only update if current shift_type of partner
            # != shift_type of ticket
            if ticket_shift_type != partner_shift_type:
                partner.shift_type = ticket_shift_type

    @api.multi
    def check_update_partner_shift_type(self):
        today = fields.Date.context_today(self)
        for record in self:
            if record.date_begin <= today:
                if record.date_end and record.date_end >= today:
                    record.update_partner_shift_type()
                elif not record.date_end:
                    record.update_partner_shift_type()

    @api.multi
    def write(self, vals):
        res = super(ShiftTemplateRegistrationLine, self).write(vals)
        self.check_update_partner_shift_type()
        return res

    @api.model
    def create(self, vals):
        res = super(ShiftTemplateRegistrationLine, self).create(vals)
        res.check_update_partner_shift_type()
        return res

    @api.model
    def cron_update_partner_shift_type(self):
        today = fields.Date.to_string(fields.Date.context_today(self))
        template_env = self.env['shift.template.registration.line']

        # Use SQL here to filter only record
        # have partner.shift_type != registration.line.shift_type
        # to get high performance
        SQL = """
            SELECT STRL.id
            FROM shift_template_registration_line STRL
            LEFT JOIN res_partner RP ON STRL.partner_id=RP.id
            LEFT JOIN shift_template_registration STR
            ON STRL.registration_id=STR.id
            LEFT JOIN shift_template_ticket STT
            ON STR.shift_ticket_id=STT.id
            WHERE
            (STRL.date_begin <= %s)
            AND (STRL.date_end >= %s OR STRL.date_end is NULL)
            AND RP.shift_type != STT.shift_type
        """
        _logger.info(">>>>> START cron_update_partner_shift_type:")
        self.env.cr.execute(SQL, (today, today))
        line_ids = [x[0] for x in self.env.cr.fetchall()]
        _logger.debug(
            ">>>>> cron_update_partner_shift_type - total: %s - line ids: %s",
            len(line_ids), line_ids
        )

        # update data by normal ORM method
        tmpl_registation_lines = template_env.search([('id', 'in', line_ids)])
        tmpl_registation_lines.update_partner_shift_type()
        _logger.info(">>>>> STOP cron_update_partner_shift_type:")
