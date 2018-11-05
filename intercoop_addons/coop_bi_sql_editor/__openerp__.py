# -*- coding: utf-8 -*-

{
    'name': 'Coop BI SQL Editor',
    'summary': "BI Views builder, based on Materialized or Normal SQL Views(Customized)",
    'version': '9.0.1.1.0',
    'license': 'AGPL-3',
    'category': 'Reporting',
    'depends': [
        'coop_base',
        'bi_sql_editor',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/menu.xml',
    ],
    'installable': True
}
