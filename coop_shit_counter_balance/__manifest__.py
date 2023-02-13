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
    'name': 'Coop Shift - Balance Counter Event',
    'summary': 'Balance The Counter Event',
    'version': '12.0.1.0.0',
    'category': 'Tools',
    'website': 'https://trobz.com',
    'author': 'Trobz',
    'license': 'AGPL-3',
    'depends': [
        'coop_shift',
    ],
    'data': [
        'data/ir_cron.xml',
    ],
    'installable': True,
}
