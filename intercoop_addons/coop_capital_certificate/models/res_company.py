# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    capital_certificate_header = fields.Char(
        "Capital Certificate Header",
        help="example: 'La S.A.S. Coopérative à Capital Variable LA LOUVE'")
    signature = fields.Binary("Signature", attachment=True)
