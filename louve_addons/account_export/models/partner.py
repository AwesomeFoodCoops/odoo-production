# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author Julien Weste - La Louve 2016
#    Inspired by Smile (smile_export_sage_100)
#    and GRAP (account_export_ebp)
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

from openerp import fields, models


class res_partner(models.Model):
    _inherit = "res.partner"

    property_account_receivable_software = fields.Char(
        'Account Receivable (software)', size=17,
        help='Receivable account in your accounting software')
    property_account_payable_software = fields.Char(
        'Account Payable (software)', size=17,
        help='Payable account in your accounting software')
