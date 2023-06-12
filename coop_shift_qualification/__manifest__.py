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
    'name': 'Coop Shift Qualification',
    'summary': 'Coop Shift Qualification',
    'version': '12.0.1.0.0',
    'category': 'Custom',
    'website': 'https://trobz.com',
    'author': 'Trobz',
    'license': 'AGPL-3',
    'depends': [
        'coop_membership',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/res_partner_qualification.xml',
        'views/res_partner_qualification_view.xml',
        'views/res_partner_view.xml',
        'views/report_timesheet_templates.xml',
        'views/res_config_view.xml',
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
