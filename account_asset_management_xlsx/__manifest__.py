# Copyright (C) 2018-Today: La Louve (<https://cooplalouve.fr>)
# @author: Simon Mas (linkedin.com/in/simon-mas)
# Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Account Asset Management xlsx",
    "version": "12.0.1.0.0",
    "category": "Accounting",
    "summary": "account_asset_management_xlsx",
    "author": "Simon Mas,  Ân Lê Hoàng",
    "website": "https://cooplalouve.fr",
    "license": "AGPL-3",
    "depends": [
        "account_asset_management",
        "report_xlsx",
    ],
    "data": [
        "report/report_account_asset_xlsx.xml",
        "wizard/account_asset_xlsx_wizard.xml",
    ],
    "installable": True,
}
