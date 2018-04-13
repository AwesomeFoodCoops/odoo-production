# -*- encoding: utf-8 -*-
{
    'name': 'Account Bank Statement Import',
    'category': 'Banking addons',
    'version': '8.0.1.0.1',
    'author': 'OpenERP SA,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/bank-statement-import',
    'depends': ['account'],
    'data': [
        "views/account_config_settings.xml",
        'views/account_bank_statement_import_view.xml',
    ],
    'demo': [
        'demo/fiscalyear_period.xml',
        'demo/partner_bank.xml',
    ],
    'auto_install': False,
# CAUTION: this module was renamed in the 9.0 branch to avoid conflicts with the
# upstream account_bank_statement_import module added in odoo 9. Exercise caution
# when porting.
    'installable': False,
}
