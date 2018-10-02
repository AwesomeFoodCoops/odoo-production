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

from openerp import api, fields, models, _
from openerp.addons import decimal_precision as dp
from openerp.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def name_get(self):
        """Return the product name without ref when the
        name_get is called from order planning form
        """
        res = []
        if self.env.context.get('order_planning_context'):
            for record in self:
                res.append((record['id'], record['name']))
        else:
            res = super(ProductProduct, self).name_get()

        return res


class ProductTemplate(models.Model):
    _inherit = "product.template"


    default_packaging = fields.Float('Default packaging',digits=dp.get_precision('Product Price'), default=1.0)

    @api.multi
    @api.constrains('default_packaging')
    def check_default_packaging(self):
        for p in self:
            if p.default_packaging <= 0.0:
                raise UserError(_("Default packaging of %s must be positive ! " % (p.name,)))




