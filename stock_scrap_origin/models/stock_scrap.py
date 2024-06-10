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

from odoo import api, fields, models
from odoo.tools import safe_eval


class StockScrap(models.Model):
    _inherit = 'stock.scrap'

    scrap_origin_id = fields.Many2one(
        comodel_name="stock.scrap.origin",
        string="Origin",
        states={'done': [('readonly', True)]}
    )
    scrap_origin_required = fields.Boolean(
        compute="_compute_scrap_origin_required"
    )

    # Depend on scrap_qty to make its value triggered when onchange
    @api.depends("scrap_qty")
    def _compute_scrap_origin_required(self):
        icp_sudo = self.env['ir.config_parameter'].sudo()
        scrap_origin_required = safe_eval(icp_sudo.get_param(
            'scrap_order.scrap_origin_required', 'False'))
        self.update({"scrap_origin_required": scrap_origin_required})
