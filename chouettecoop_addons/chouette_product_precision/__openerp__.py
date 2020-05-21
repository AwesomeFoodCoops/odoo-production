# -*- coding: utf-8 -*-
{
    'name': 'Chouette Default Precision for Products',
    'version': '9.0.0.0.0',
    'category': 'Custom',
    'description': """
Sets 3 digits precision for Volume and Net Weight on products
    """,
    'author': 'La Chouette Coop',
    'website': 'https://lachouettecoop.fr',
    'license': 'AGPL-3',
    'depends': [
        'coop_default_pricetag',
    ],
    'data': [
        'data/decimal_precision_data.xml',
    ],
}

