# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'EDI Purchase',
    'version': '9.0.1.0.2',
    'category': 'Custom',
    'author': 'Druidoo',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': ['purchase', 'edi_purchase_config'
    ],
    'data': ['data/ir_cron.xml',
             'views/supplier_price_list_view.xml',
             'views/actions.xml',
             'views/product_template_view.xml'

    ],
}
