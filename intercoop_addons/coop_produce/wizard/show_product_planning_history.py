# -*- coding: utf-8 -*-
##############################################################################
#
#    Purchase - Computed Purchase Order Module for Odoo
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



from openerp import api, models, fields, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import UserError


import logging

_logger = logging.getLogger(__name__)

class PlanificationProductHistory(models.TransientModel):
    _name = "planification.product.history"
    _description = "Product history planning"

    product_id = fields.Many2one('product.product', 'Product', required=True)
    default_packaging = fields.Float('Default packaging', related='product_id.default_packaging')
    line_ids = fields.Many2many('order.week.planning.line', string="History")

    @api.model
    def default_get(self, fields):
        context = self._context or {}
        res = super(PlanificationProductHistory, self).default_get(fields)
        line_ids = self.env.context.get('line_ids',[])
        product_id = self.env.context.get('product_id',False)
        res.update({
                'product_id':product_id,
                'line_ids':[(6,0,line_ids)]
        })
        return res

    @api.multi
    def init_display_from_date(self,date):
        raise UserError(_("Not yet implemented"))

