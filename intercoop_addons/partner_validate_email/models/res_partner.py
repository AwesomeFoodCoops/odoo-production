# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from openerp import api, fields, models, tools, _
from openerp.exceptions import Warning
import logging
from openerp.tools.safe_eval import safe_eval
try:
    from validate_email import validate_email
    from DNS import TimeoutError
except ImportError:
    validate_email = None

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def validate_email_address(self, email):
        '''
        @Function validate email.
            - Validate email format with regex.
            - Use library validate_email to check email exist or not.
        '''
        disable = self._context.get('disable_validate_email', False)
        config_param_env = self.env['ir.config_parameter']
        email_temp = email and re.sub('\s', '', email)
        valid = True
        message = ""
        if tools.single_email_re.match(email_temp):
            if disable:
                return email
            message = _("Email format correct.\n")
            avail_check = config_param_env.get_param('validate_email',
                                                     'False')
            avail_check = safe_eval(avail_check)
            if not validate_email or not avail_check:
                return email_temp
            else:
                try:
                    valid = validate_email(email,
                                           check_mx=True,
                                           verify=True)
                except TimeoutError as toe:
                    # time out when checking validating email domain.
                    # It still be correct so pass this case.
                    valid = True
                    _logger.warn("[TimeoutError] - time out when checking " +
                                 "email '%s' - partner_id=" % (email, self.id))
        elif email_temp:
            valid = False
        else:
            # this case happen when user input all space in this field.
            valid = True
        if valid:
            return email_temp
        else:
            if not message:
                raise Warning(_("Email format is incorrect."))
            else:
                raise Warning(_("Email format is correct but domain " +
                                "doesn't seem to have any mail server."))

    @api.model
    def create(self, vals):
        email = vals.get('email', False)
        if email:
            vals.update({'email': self.validate_email_address(email)})
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        email = vals.get('email', False)
        if email:
            vals.update({'email': self.validate_email_address(email)})
        return super(ResPartner, self).write(vals)