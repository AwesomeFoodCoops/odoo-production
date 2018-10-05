# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Lorenzo Battistini <lorenzo.battistini@agilebg.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp import models, api

import logging
import re
import socket
from email.message import Message

from openerp import tools
from openerp.addons.mail.models.mail_message import decode
from openerp.tools.safe_eval import safe_eval as eval


_logger = logging.getLogger(__name__)


mail_header_msgid_re = re.compile('<[^<>]+>')


def decode_header(message, header, separator=' '):
    return separator.join(map(decode, filter(None, message.get_all(header, []))))


class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    @api.model
    def verify_memberspace_alias(self, message, header, user_sent, email_from):
        MemberSpaceAlias = self.env['memberspace.alias']
        Alias = self.env['mail.alias']
        alias_error = MemberSpaceAlias
        alias_pass = MemberSpaceAlias
        mail_tmpl = self.env.ref(
            'coop_memberspace.email_inform_cannot_send_to_memberspace_alias')
        if not message.has_key(header):
            return alias_error, alias_pass
        rcpt_tos = ','.join([decode_header(message, header)])
        local_parts = [e.split('@')[0].lower()
            for e in tools.email_split(rcpt_tos)]
        aliases = Alias.search([('alias_name', 'in', local_parts)])
        memberspace_aliases = MemberSpaceAlias.search([
            ('alias_id', 'in', aliases.ids)])
        for memberspace_alias in memberspace_aliases:
            if not user_sent:
                alias_error |= memberspace_aliases
                break
            coordinators = memberspace_alias.shift_id.user_ids
            members = coordinators | memberspace_alias.shift_id.registration_ids.filtered(
                lambda r: r.is_current_participant).mapped('partner_id')
            if memberspace_alias.type == 'team' and \
                user_sent not in coordinators:
                alias_error |= memberspace_alias
                if user_sent in members and mail_tmpl:
                    email_add = memberspace_alias.alias_name + '@' + \
                        memberspace_alias.alias_domain
                    template_values = {
                        'email_to': email_from,
                        'email_from': self.env.user.company_id.email,
                        'email_cc': False,
                        'lang': user_sent.lang,
                        'auto_delete': True,
                        'partner_to': False,
                    }
                    mail_tmpl.write(template_values)
                    mail_tmpl.with_context(email_add=email_add).send_mail(
                        self.env.user.id, force_send=True)
                continue
            elif memberspace_alias.type == 'coordinator' and \
                user_sent not in members:
                alias_error |= memberspace_alias
                continue
            alias_pass |= memberspace_alias
        if alias_error:
            new_header = ','.join([ma.alias_name + '@' + ma.alias_domain
                for ma in alias_pass])
            message.replace_header(header, new_header)
        return alias_error, alias_pass

    @api.model
    def message_route(self, message, message_dict, model=None,
            thread_id=None, custom_values=None):
        if not isinstance(message, Message):
            raise TypeError('message must be an email.message.Message at this point')
        email_from = decode_header(message, 'From')
        # Memberspace workflow
        if '<' in email_from:
            email_from = email_from.split('<')[1][:-1]
        user_send_email = self.env['res.partner'].search([
            ('email', '=', email_from)
        ], limit=1)
        error_memberspace_aliases = self.env['memberspace.alias']
        pass_memberspace_aliases = self.env['memberspace.alias']
        # Check header with key = To
        alias_error, alias_pass = self.verify_memberspace_alias(
            message, 'To', user_send_email, email_from)
        pass_memberspace_aliases |= alias_pass
        error_memberspace_aliases |= alias_error
        # Check header with key = Delivered-To
        alias_error, alias_pass = self.verify_memberspace_alias(
            message, 'Delivered-To', user_send_email, email_from)
        pass_memberspace_aliases |= alias_pass
        error_memberspace_aliases |= alias_error
        # Check header with key = Cc
        alias_error, alias_pass = self.verify_memberspace_alias(
            message, 'Cc', user_send_email, email_from)
        pass_memberspace_aliases |= alias_pass
        error_memberspace_aliases |= alias_error
        # Check header with key = Resent-To
        alias_error, alias_pass = self.verify_memberspace_alias(
            message, 'Resent-To', user_send_email, email_from)
        pass_memberspace_aliases |= alias_pass
        error_memberspace_aliases |= alias_error
        # Check header with key = Resent-Cc
        alias_error, alias_pass = self.verify_memberspace_alias(
            message, 'Resent-Cc', user_send_email, email_from)
        pass_memberspace_aliases |= alias_pass
        error_memberspace_aliases |= alias_error
        
        if not pass_memberspace_aliases:
            return []
        return super(MailThread, self).message_route(
            message, message_dict, model=model, thread_id=thread_id,
            custom_values=custom_values)
