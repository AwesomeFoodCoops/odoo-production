# -*- coding: utf-8 -*-
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import fields
from openerp.osv.orm import Model


class product_uom(Model):
    _inherit = 'product.uom'

    # Column Section
    _columns = {
        'scale_type': fields.char(
            string='Scale Type'),
    }
