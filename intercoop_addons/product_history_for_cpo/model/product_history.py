# *- encoding: utf-8 -*-
##############################################################################
#
#    Product - Average Consumption Module for Odoo
#    Copyright (C) 2013-Today GRAP (http://www.grap.coop)
#    @author Julien WESTE
#    @author Sylvain LE GAL (https://twitter.com/legalsylvain)
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

from openerp import models, api


class ProductHistory(models.Model):
    _inherit = "product.history"

# Private section
    @api.multi
    def ignore_line_cpo(self):
        self.mark_line(True)
        context = self.env.context
        model = context.get('active_model', False)
        id = context.get('active_id', False)
        cpol = self.env[model].browse(id)
        cpol.displayed_average_consumption =\
            self.product_id.displayed_average_consumption
        cpol.view_history()

    @api.multi
    def unignore_line_cpo(self):
        self.mark_line(False)
        context = self.env.context
        model = context.get('active_model', False)
        id = context.get('active_id', False)
        cpol = self.env[model].browse(id)
        cpol.displayed_average_consumption =\
            self.product_id.displayed_average_consumption
        cpol.view_history()
