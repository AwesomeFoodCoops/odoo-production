# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    'name': 'Account Bank Reconciliation Rule',
    'version': '9.0.1.0.11',
    'category': 'Account',
    'description': """
        A new rule is applied when doing bank reconciliation:
        -   if account_code of account.move.line = account_code of bank.statement.line  => the transaction is matched, 
        -   if account_code of account.move.line != account_code of bank.statement.line => a new move is generated,
            move.line on source account is allocated and counterpart on bank journal account is matched to the statement.
    """,

    'license': 'AGPL-3',
    'depends': [
        'account'
    ],
    'data': [
    ],
}
