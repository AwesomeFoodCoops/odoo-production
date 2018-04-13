# -*- coding: utf-8 -*-
##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2014 Aurélien DUMAINE
#    Copyright (C) 2015 Akretion (www.akretion.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields


class PosConfig(models.Model):
    _inherit = 'pos.config'

    iface_automatic_cashdrawer = fields.Boolean(
        'Automatic cashdrawer',
        help="An automatic cashdrawer is available on the Proxy")

    iface_automatic_cashdrawer_ip_address = fields.Char('Automatic cashdrawer IP address')
    iface_automatic_cashdrawer_tcp_port = fields.Char('Automatic cashdrawer TCP port') # WARNING : set a port bigger than 1024 to allow a non-root user to listen on it
    iface_automatic_cashdrawer_display_accept_button = fields.\
        Boolean('Automatic cashdrawer display accept button', default=False)
    iface_automatic_cashdrawer_screen_on_top = fields.\
        Boolean('Automatic cashdrawer screen on top', default=False)
