##############################################################################
#
#    Copyright since 2009 Trobz (<https://trobz.com/>).
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

{
    'name': 'Scrap Report',
    'summary': 'Display scrap products.',
    'version': '12.0.1.0.0',
    'category': 'Warehouse',
    'website': 'https://github.com/OCA/stock-logistics-reporting',
    'author': 'Trobz',
    'license': 'AGPL-3',
    'depends': [
        'stock_account',
        'stock_scrap_origin',
        'report_xlsx_helper',
    ],
    'data': [
        'report_data.xml',
        'scrap_report_menu.xml',
        'stock_scrap_product_wizard_view.xml',
    ],
    'installable': True,
}
