# -*- coding: utf-8 -*-
# Copyright (C) 2013-Today: GRAP (http://www.grap.coop)
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Stock - Expense Transfer',
    'version': '9.0.1.0.0',
    'category': 'Accounting & Finance',
    'author': 'GRAP, La Louve, Odoo Community Association (OCA)',
    'website': 'http://www.grap.coop',
    'depends': [
        'stock',
        'account',
    ],
    'data': [
        'views/view_stock_picking.xml',
        'views/action.xml',
        'views/menu.xml',
        'views/view_stock_move.xml',
        'views/view_stock_picking_type.xml',
        'views/view_stock_picking_wizard_expense_transfer.xml',
    ],
    'demo': [
        'demo/account_account.xml',
        'demo/stock_location.xml',
        'demo/ir_sequence.xml',
        'demo/stock_picking_type.xml',
    ],
    'installable': True,
}
