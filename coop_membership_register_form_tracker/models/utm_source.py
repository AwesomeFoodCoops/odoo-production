# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class UtmSource(models.Model):
    _inherit = "utm.source"

    is_for_discovery_meeting = fields.Boolean()

    def _get_member_register_sources(self):
        args = [("is_for_discovery_meeting", "=", True)]
        limit = int(self.env['ir.config_parameter'].sudo().\
            get_param("register_form.source.limit", 0))
        if limit == 0:
            limit = None
        return self.search(args, limit=limit)
