
from odoo.addons.coop_membership.controllers.main import WebsiteRegisterMeeting
from odoo.http import request



class WebsiteRegisterMeetingTracker(WebsiteRegisterMeeting):
    def _prepare_partner_val(self, partner_val, **post):
        partner_val = super()._prepare_partner_val(partner_val, **post)
        # Add UTM Sources
        source_ids = self._parse_sources(post)
        if source_ids:
            partner_val["utm_source_ids"] = [(6, 0, source_ids)]
        return partner_val

    def _prepare_register_form_vals(self, vals):
        vals = super()._prepare_register_form_vals(vals)
        # Add utm.source
        source_datas = request.env['utm.source']._get_member_register_sources()
        vals["source_datas"] = source_datas
        vals["company_name"] = request.env.user.company_id.name
        return vals

    def _parse_sources(self, post):
        """
        """
        sids = []
        if not post:
            return sids
        prefix = "select_sources-"
        keys = post.keys()
        for k in keys:
            if not k.startswith(prefix):
                continue
            sids.append(int(post.get(k)))
        # Check other source
        if post.get("other_source"):
            source = request.env['utm.source'].create({"name": post["other_source"]})
            sids.append(source.id)
        return sids
