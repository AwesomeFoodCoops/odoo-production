# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

{
    "name": "EDI Purchase DIAPAR",
    "version": "12.0.1.0.0",
    "category": "Custom",
    "author": "Druidoo",
    "website": "http://www.druidoo.io",
    "license": "AGPL-3",
    "depends": [
        "product",
        "edi_purchase_config",
        "edi_purchase_base",
        "purchase_package_qty",
        "coop_purchase",
        "coop_membership",
    ],
    "data": [
        "wizard/invoice_supplier_price_update.xml",
        "views/res_partner_view.xml",
    ],
}
