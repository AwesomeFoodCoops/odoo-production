# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class UtmSource(models.Model):
    _inherit = "utm.source"
    _order="sequence"

    sequence = fields.Integer(default=10)
    is_for_discovery_meeting = fields.Boolean()
    category_id = fields.Many2one("utm.source.category")

    def _get_member_register_sources(self):
        args = [("is_for_discovery_meeting", "=", True)]
        limit = int(self.env['ir.config_parameter'].sudo().\
            get_param("register_form.source.limit", 0))
        if limit == 0:
            limit = None
        sources = self.search(args, limit=limit)
        wo_category_sources = sources.filtered(
            lambda s: not s.category_id
        )
        w_category_sources = sources - wo_category_sources
        category_sources_dict = {}
        for source in w_category_sources:
            category = source.category_id.display_name
            if category in category_sources_dict:
                category_sources_dict[category] |= source
            else:
                category_sources_dict[category] = source

        return (
            wo_category_sources,
            category_sources_dict.keys(),
            category_sources_dict
        )
