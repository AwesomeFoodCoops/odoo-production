# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Account Bank Statement Summary',
    'version': '9.0.1.0.11',
    'category': 'Account',
    'author': 'Odoo Community Association (OCA), Druidoo',
    'license': 'AGPL-3',
    'depends': [
        'report_xlsx', 'account'
    ],
    'data': [
        "report/report_bank_reconciliation_summary_view.xml",
        "wizard/bank_reconciliation_summary_wizard.xml",
        "views/account_journal_views.xml",
    ],
}
