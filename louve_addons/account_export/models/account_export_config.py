# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author Julien Weste - La Louve 2016
#    Inspired by Smile (smile_export_sage_100)
#    and GRAP (account_export_ebp)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models


class AccountExportConfig(models.Model):
    _name = 'account.export.config'

    name = fields.Char('Name', required=True)
    header = fields.Char("Header", help="""Header of the exported file.
        exemple: journal,account,ref,amount""")
    footer = fields.Char("Footer", help="""Footer of the exported file.
        exemple: END""")
    dateformat = fields.Char(
        string='Software Date Format',
        help="""
        %d: day on 2 digits
        %m: month on 2 digits
        %y: year on 2 digits
        %Y: year on 4 digits
        exemple: %d%m%y -> 211216""")
    # fields_to_export = fields.One2many(
    #     string='Fields to export', comodel_name='ir.model.fields',
    #     domain=[('model', '=', 'account.move.line')])
    is_default = fields.Boolean('Is Default')
    active = fields.Boolean('active', default=True)
