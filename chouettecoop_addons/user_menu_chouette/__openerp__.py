# -*- coding: utf-8 -*-
##############################################################################
#
#    Require User Login, Odoo addon
#    Copyright La Chouette Coop
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
    'name'       : "User Menu for La Chouette Coop",
    'summary'    : "Replace top right UserMenu: change support link, remvoe My Odoo Account link",
    'category'   : 'Extra Tools',
    'author'     : "La Chouette Coop",
    'website'    : "http://www.lachouettecoop.fr",
    'license'    : "AGPL-3",
    'version'    : '9.0.0.0.1',
    'installable': True,
    'depends'    : [
        'base_setup',
        'base',
        'web',
    ],
    'data'       : [
        'data/user_menu_chouette.xml',
        'views/res_config_view.xml',
    ],
    'qweb'       : [
        'static/src/xml/base.xml',
    ],
}
