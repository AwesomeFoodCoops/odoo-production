# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class ResPartnerGenerateBarcodeWizard(models.TransientModel):
    _inherit = 'res.partner.GenerateBarcode.wizard'

    def _default_partner_id(self):
        return self.env.context.get('active_id', False)

    # Column Section
    partner_id = fields.Many2one(
        comodel_name='res.partner', default=_default_partner_id,
        required=True, readonly=True)

    current_barcode = fields.Char(
        related='partner_id.barcode', readonly=True)

    @api.multi
    def generate_barcode(self):
        for wizard in self:
            pass
            # TODO
