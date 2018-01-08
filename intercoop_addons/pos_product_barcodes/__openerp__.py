# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.cooplalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


{
    'name': 'Coop - PoS Product Barcodes',
    'version': '9.0.2.0.0',
    'category': 'Custom',
    'summary': 'Custom Barcode Rules for Coop article weight and price.',
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'depends': [
        'base',
        'barcodes', 
        'stock',
        'point_of_sale',
    ],
    'data': [
        # Classical Data

        # Custom Data
        'data/barcode_rule.xml',
    ],
    'installable': True,
}
