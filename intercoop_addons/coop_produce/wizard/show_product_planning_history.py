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

import datetime
from dateutil import relativedelta
import json
import time
import sets

import openerp
from openerp.osv import fields, osv
from openerp.tools.float_utils import float_compare, float_round
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from openerp import SUPERUSER_ID, api, models
import openerp.addons.decimal_precision as dp
from openerp.addons.procurement import procurement

import sys

reload(sys)
sys.setdefaultencoding('utf8')

import logging

_logger = logging.getLogger(__name__)

class PlanificationHistoriqueProduit(osv.osv):
    _name = "planification.product.history"
    _description = "Product History"

    _columns = {

        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'default_packaging': fields.float('Default packaging', digits_compute=dp.get_precision('Product Unit of Measure')),
        'line_ids': fields.one2many('planification.product.history.line', 'history_id', 'Historique',
                                    help="Historique Lines."),
    }

class PlanificationHistoriqueProduitLine(osv.osv):
    _name = "planification.product.history.line"
    _description = "Product History Line"

    _columns = {
        'history_id': fields.many2one('planification.product.history', 'Product History', ondelete='cascade',
                                      select=True),
        'semaine_nbre': fields.integer('Week Number'),
        'prix_unitaire': fields.float('Unit Price', digits_compute=dp.get_precision('Order Week Planning Precision')),
        's_inv': fields.float('S Inv', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'monday_line': fields.float('Mond', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'tuesday_line': fields.float('Tues', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'wednesday_line': fields.float('Wed', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'inv_int': fields.float('Inv Int', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'thirsday_line': fields.float('Thurs', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'friday_line': fields.float('Fri', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'saturday_line': fields.float('Sat', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'total_inv': fields.float('Total + S Inv', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'e_inv': fields.float('E Inv', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'loss': fields.float('Loss', digits_compute=dp.get_precision('Order Week Planning Precision')),
        'sold': fields.float('Sold', digits_compute=dp.get_precision('Order Week Planning Precision')),
    }
