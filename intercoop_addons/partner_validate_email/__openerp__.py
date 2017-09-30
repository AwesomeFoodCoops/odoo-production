# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve (<http://www.lalouve.net/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Partner - Validate Email',
    'version': '9.0.0.0.0',
    'category': 'base',
    'description': """
Partner - Validate Email
===========================================================================

Validate email address syntax with regex and optional choice for validating
with checking MX (Mail Exchanger)

Required library
----------------
* Python lib validate_email (https://pypi.python.org/pypi/validate_email)
Execution

    pip install validate_email

    pip install pyDNS

* This module will validate partner email with settings as :
    * Enable verification of domain when checking an email address.
    * Go to Settings >> General Settings
    * Tick on "Validate email address"

Copyright, Author and Licence :
-------------------------------
* Author :
    * La Louve (<http://www.lalouve.net/>)
* Licence : AGPL-3 (http://www.gnu.org/licenses/)
    """,
    'author': 'La Louve',
    'website': 'http://www.lalouve.net',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
    ],
    'data': [
        'views/res_config_view.xml',
    ],
}
