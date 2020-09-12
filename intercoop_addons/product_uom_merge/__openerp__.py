# -*- coding: utf-8 -*-
{
    'name': 'Product UoM Merge',
    'version': '9.0.1.0.0',
    'depends': ['product'],
    "author": "Druidoo",
    'description': "Provides a mechanism to safely merge UoMs",
    "category": 'Stock',
    "sequence": 10,
    "license": "AGPL-3",
    'data': [
        "security/ir.model.access.csv",
        'wizard/product_uom_merge.xml',
    ],
}
