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

from openerp import api, fields, models

class user_menu_chouette_config_settings(models.TransientModel):
    """ Inherit the base setting to add the url to use for User Menu «Support» link. """

    _inherit = 'base.config.settings'

    x_user_menu_support_url = fields.Char("Menu Support", help="Lien «Support» dans le menu utilisateur")

    @api.multi
    def get_default_x_user_menu_support_url(self):
        url = self.env["ir.config_parameter"].get_param("x_user_menu_support_url", default=None)
        return { 'x_user_menu_support_url': url or False }

    @api.multi
    def set_x_user_menu_support_url(self):
        for record in self:
            self.env['ir.config_parameter'].set_param("x_user_menu_support_url", self.x_user_menu_support_url or '')

