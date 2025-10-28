
from odoo.addons.coop_membership.controllers.main import WebsiteRegisterMeeting
from odoo.http import request



class WebsiteRegisterMeetingTracker(WebsiteRegisterMeeting):
    def _prepare_partner_val(self, partner_val, **post):
        partner_val = super()._prepare_partner_val(partner_val)
        # Add source_id
        if post.get("select_source"):
            partner_val["source_id"] = post["select_source"]
        return partner_val

    def _prepare_register_form_vals(self, vals):
        vals = super()._prepare_register_form_vals(vals)
        # Add utm.source
        sources = request.env['utm.source']._get_member_register_sources()
        vals["sources"] = sources
        return vals
