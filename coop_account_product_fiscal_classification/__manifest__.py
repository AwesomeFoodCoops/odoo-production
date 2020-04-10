# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Product - Fiscal Classification',
    'summary': 'Provide extra features for Fiscal Classification',
    'version': '12.0.1.0.0',
    'category': 'Accounting',
    'author': 'Druidoo',
    'website': 'https://www.druidoo.io',
    'license': 'AGPL-3',
    'depends': [
        'account_product_fiscal_classification'
    ],
    'data': [
        'views/product_template_view.xml',
        'views/account_product_fiscal_classification_view.xml'
    ],
    'demo': [
    ],
    'installable': True,
}
