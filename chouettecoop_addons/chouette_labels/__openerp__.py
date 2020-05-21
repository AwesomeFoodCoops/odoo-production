# -*- coding: utf-8 -*-
{
    'name': 'Chouette Report for Labels',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'description': """
Add report functionality for printing labels for products with format chosen by La Chouette Coop
    """,
    'author': 'La Chouette Coop',
    'website': 'https://lachouettecoop.fr',
    'license': 'AGPL-3',
    'depends': [
        'coop_default_pricetag',
    ],
    'data': [
        'data/report_paperformat.xml',
        'data/pricetag_model.xml',
        'data/product_category_print.xml',
        'report/lcc_product_report.xml',
        'report/report_pricetag_lcc.xml',
    ],
}

