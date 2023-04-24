import odoo
from odoo import http
from odoo.http import request

UPDATE_PHONE = ["mobile", "phone"]

UPDATE_ADDRESS = ["street", "city", "zip"]


class Website(odoo.addons.website.controllers.main.Website):
    @http.route(
        "/edit-phone", type="http", auth="user", website=True, methods=["POST"]
    )
    def edit_phone(self, **kw):
        new_value = {}
        for field in list(x for x in UPDATE_PHONE if x in kw):
            new_value.update({field: kw.get(field, False)})
        request.env.user.partner_id.write(new_value)
        return http.local_redirect("/profile")

    @http.route(
        "/edit-address",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def edit_address(self, **kw):
        new_value = {}
        for field in list(x for x in UPDATE_ADDRESS if x in kw):
            new_value.update({field: kw.get(field, False)})
        request.env.user.partner_id.write(new_value)
        return http.local_redirect("/profile")

    @http.route(
        "/edit-email-pos-receipt",
        type="http",
        auth="user",
        website=True,
        methods=["POST"],
    )
    def edit_email_pos_receipt(self, **kw):
        request.env.user.partner_id.write(
            {"email_pos_receipt": kw.get("email_pos_receipt", False),
            "no_email_pos_receipt": not kw.get("email_pos_receipt", False)}
        )
        return http.local_redirect("/profile")
