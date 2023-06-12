##############################################################################
#
#    Copyright since 2009 Trobz (<https://trobz.com/>).
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

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Partner(models.Model):
    _inherit = 'res.partner'

    qualification_ids = fields.Many2many(
        "res.partner.qualification",
        inverse="_update_shift_leader"
    )
    is_qual_leader = fields.Boolean(
        compute="compute_qual_leader",
        store=True
    )
    qualifications = fields.Char(
        compute="compute_qual_leader",
        store=True,
    )

    def _get_leader_ftop_warning(self, shift_templates):
        self.ensure_one()
        msg = None
        if not shift_templates or self.in_ftop_team:
            msg = _(
                "A coordinator must already be assigned to an ABCD team"
            )
        return msg

    def _update_shift_leader(self):
        for partner in self:
            if partner.is_qual_leader:
                # Check Standard
                shift_templates = partner.tmpl_reg_ids.filtered(
                    "is_current_participant").mapped("shift_template_id")
                warn_msg = partner._get_leader_ftop_warning(shift_templates)
                if warn_msg:
                    raise ValidationError(warn_msg)

                # Update leaders
                partner.template_ids |= shift_templates
                shifts = partner.template_ids.mapped("shift_ids").filtered(
                    lambda s: s.state != "done")
                for shift in shifts:
                    shift.user_ids |= partner
            elif partner.template_ids:
                # Remove leaders
                shifts = partner.template_ids.mapped("shift_ids").filtered(
                    lambda s: s.state != "done")
                for shift in shifts:
                    shift.user_ids -= partner
                partner.template_ids = False

    @api.depends("qualification_ids", "qualification_ids.is_leader")
    def compute_qual_leader(self):
        for rec in self:
            is_leader = any(q.is_leader for q in rec.qualification_ids)
            rec.is_qual_leader = is_leader
            rec.qualifications = ", ".join(rec.qualification_ids.mapped("name"))
