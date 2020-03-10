# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteValidationEmail(http.Controller):

    @http.route(['/validate/<int:partner_id>/<string:email_validation_string>'],
                type='http', auth="none", website=True)
    def validate_string_email(self, partner_id, email_validation_string, **kwargs):
        REGISTER_USER_ID = \
            int(request.env['ir.config_parameter'].sudo(
            ).get_param('register_user_id'))
        partner = request.env['res.partner'].sudo(REGISTER_USER_ID).browse(partner_id)

        if partner:
            partner.check_email_validation_string(email_validation_string)
            if partner.is_checked_email:
                return request.render(
                    "email_validation_check.confirm_success")
            else:
                return request.render(
                    "email_validation_check.confirm_failed")
