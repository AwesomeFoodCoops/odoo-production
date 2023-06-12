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


QUAL_CHAR_LIMIT = 5

class PartnerQualification(models.Model):
    _name = 'res.partner.qualification'
    _description = 'Partner Quailification'
    _order = "seq"

    name = fields.Char(required=True, default="/")
    is_leader = fields.Boolean()
    seq = fields.Integer(string="Sequence")
    can_be_leader = fields.Boolean(compute="comute_can_be_leader")

    @api.constrains("name")
    def constrains_name(self):
        for rec in self:
            if rec.name and len(rec.name) > QUAL_CHAR_LIMIT:
                raise ValidationError(_(
                    "Qualification must be limited to {limit} characters"
                ).format(
                    limit=QUAL_CHAR_LIMIT
                ))

    @api.depends("name")
    def comute_can_be_leader(self):
        get_param = self.env["ir.config_parameter"].sudo().get_param
        nb_of_leader = get_param("coop_shift_qualification.nb_of_leader", 1)
        reg_nb_of_leader = self.env["res.partner.qualification"].\
            search_count([("is_leader", "=", True)])
        for rec in self:
            rec.can_be_leader = rec.is_leader or \
                nb_of_leader > reg_nb_of_leader

    @api.constrains("is_leader")
    def constrains_is_leader(self):
        for rec in self:
            if not rec.is_leader:
                continue
            get_param = self.env["ir.config_parameter"].sudo().get_param
            nb_of_leader = get_param("coop_shift_qualification.nb_of_leader", 1)
            reg_nb_of_leader = self.env["res.partner.qualification"].\
                search_count([("is_leader", "=", True)])
            if nb_of_leader < reg_nb_of_leader:
                raise ValidationError(_(
                    "'Nb of Leader' of Qualification must be limited to {l}"
                ).format(
                    l=nb_of_leader
                ))

    @api.model
    def _update_partner_qualification(self):
        rec = self.search([
            ("is_leader", "=", True)
        ], limit=1)
        if not rec:
            return
        templates = self.env["shift.template"].search(
            [("is_ftop", "=", False)])
        for tmpl in templates:
            tmpl.update_qualification(tmpl.user_ids, raise_error=False)

