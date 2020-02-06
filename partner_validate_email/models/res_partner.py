# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import re
from odoo import api, models, tools, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

try:
    from validate_email import validate_email
except ImportError:
    _logger.error('Unable to import validate_email')
    validate_email = None

try:
    import DNS
except ImportError:
    _logger.error('Unable to import DNS. "py3dns" library is required')
    DNS = None


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def validate_email_address(self, email):
        '''
        @Function validate email.
            - Validate email format with regex.
            - Use library validate_email to check email exist or not.
        '''
        ICP = self.env['ir.config_parameter']
        email_temp = email and re.sub(r'\s', '', email)
        valid = True
        message = ""

        if tools.single_email_re.match(email_temp):
            if self._context.get('disable_validate_email', False):
                return email
            message = _("Email format correct.\n")
            avail_check = ICP.get_param(
                'partner_validate_email.validate_email', 'False')
            if not validate_email or not safe_eval(avail_check):
                return email_temp
            else:
                try:
                    valid = validate_email(email, check_mx=True, verify=True)
                except DNS.TimeoutError:
                    # time out when checking validating email domain.
                    # It still be correct so pass this case.
                    valid = True
                    _logger.warning(
                        "[TimeoutError] - time out when checking "
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
                raise UserError(_("Email format is incorrect."))
            else:
                raise UserError(_("Email format is correct but domain " +
                                  "doesn't seem to have any mail server."))

    @api.constrains('email')
    def _check_email(self):
        self.validate_email_address(self.email)
