# -*- coding: utf-8 -*-
{
    'name': 'Chouette Default Barcode Patterns',
    'version': '9.0.1.0.0',
    'category': 'Custom',
    'description': """
Modify default barcode rules :
  - Replace Customer barcode from 42 to 24
  - Replace Weight barcode 3 decimals from 21.....{NNDDD} by 26.....{NNDDD}
    """,
    'author': 'La Chouette Coop',
    'website': 'https://lachouettecoop.fr',
    'license': 'AGPL-3',
    'depends': [
        'point_of_sale',
    ],
    'data': [
        'data/default_barcode_patterns.xml',
    ],
}

