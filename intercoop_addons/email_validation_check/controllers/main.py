# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import openerp
from openerp import http
from openerp.http import request
from openerp.addons.website.models.website import slug
from openerp.addons.web.controllers import main
from openerp import fields
import logging
import werkzeug
import requests
from datetime import datetime

_logger = logging.getLogger(__name__)


class WebsiteValidationEmail(http.Controller):

    @http.route(['/validate/<int:partner_id>/<string:email_validation_string>'],
                type='http', auth="none", website=True)
    def validate_string_email(self, partner_id, email_validation_string, **kwargs):
        REGISTER_USER_ID =\
            int(request.env['ir.config_parameter'].sudo(
            ).get_param('register_user_id'))

        partner_obj = request.registry['res.partner']
        partner = partner_obj.browse(request.cr, REGISTER_USER_ID, partner_id,
                                     context=request.context)

        if partner:
            partner.check_email_validation_string(email_validation_string)
            if partner.is_checked_email:
                return request.render(
                    "email_validation_check.confirm_success")
            else:
                return request.render(
                    "email_validation_check.confirm_failed")
