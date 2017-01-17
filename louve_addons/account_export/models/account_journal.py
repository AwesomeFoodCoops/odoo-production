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


class account_journal(models.Model):
    _inherit = "account.journal"

    export_code = fields.Char(
        'Export Account Code', size=6,
        help="Code of this journal in your accounting software")
    group_fields = fields.Many2many(
        string='Group export by', comodel_name='ir.model.fields',
        domain=[('model', '=', 'account.move.line')],
        help="""If you specify fields here, they will be used to group the
        move lines in the generated exported file.""")
