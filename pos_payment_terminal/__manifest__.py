##############################################################################
#
#    POS Payment Terminal module for Odoo
#    Copyright (C) 2014 Aurélien DUMAINE
#    Copyright (C) 2015 Akretion (www.akretion.com)
#    Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
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
{
    'name': 'POS Payment Terminal',
    'version': '12.0.0.1.0',
    'category': 'Point Of Sale',
    'summary': 'Manage Payment Terminal device from POS front end',
    'author': "Aurélien DUMAINE,Akretion,Odoo Community "
              "sdfsdfsdfdsfsdfsAssociation (OCA)",
    'license': 'AGPL-3',
    'depends': ['point_of_sale','account'],
    'data': [
        'views/pos_config.xml',
        'views/account_journal.xml',
        'views/assets.xml',
        'security/security.xml',
        'views/account_bank_statement_line_view.xml'
    ],
    'demo': ['demo/pos_config.xml'],
    'installable': True,
}
