# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    capital_certificate_header = fields.Char(
        "Capital Certificate Header",
        related='company_id.capital_certificate_header', readonly=False,
        help="example: 'La S.A.S. Coopérative à Capital Variable LA LOUVE'")
    signature = fields.Binary(
        "Signature", attachment=True, related='company_id.signature',
        readonly=False)
