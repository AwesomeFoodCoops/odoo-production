# -*- encoding: utf-8 -*-
##############################################################################
#
#    Sale - Food Module for Odoo
#    Copyright (C) 2012-Today GRAP (http://www.grap.coop)
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

from openerp.tests.common import TransactionCase
import openerp.netsvc as netsvc


class TestSaleFood(TransactionCase):
    """Tests for 'Sale Food' Module"""

    def setUp(self):
        super(TestSaleFood, self).setUp()
        self.ppw_obj = self.registry('product.pricetag.wizard')
        self.pp_obj = self.registry('product.product')
        self.iarx_obj = self.registry('ir.actions.report.xml')
        self.imd_obj = self.registry('ir.model.data')

    # Test Section
    def test_01_wizard(self):
        """Test the behaviour of wizard pricetag"""
        cr, uid = self.cr, self.uid
        pp_ids = self.pp_obj.search(cr, uid, [
            ('pricetag_state', 'in', ('1', '2'))], context=None)
        self.assertEqual(
            len(pp_ids), self.ppw_obj._needaction_count(cr, uid),
            "Incorrect computation of Needed Pricetag Quantity.")

        ppw_id = self.ppw_obj.create(cr, uid, {}, {'active_id': True})
        context = {  # noqa
            'active_model': u'product.pricetag.wizard',
            'active_ids': [ppw_id],
            'active_id': ppw_id}
        report_obj = netsvc.LocalService('report.pricetag.report')
        try:
            # This can fail on Travis System because of problem of extra
            # Dependencies of xvfb / X System
            # We assume that is the problem of the module 'webkit_report'
            # to work correctly
            report_obj.create(
                cr, uid, [ppw_id], {'report_type': u'webkit'}, context)
        except:
            pass
        self.assertEqual(
            len(pp_ids) - 14, self.ppw_obj._needaction_count(cr, uid),
            "Printing pricetag must decrease the number of products to print.")
