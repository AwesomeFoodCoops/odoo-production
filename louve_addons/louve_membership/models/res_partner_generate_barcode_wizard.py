# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from openerp import models, fields, api

_logger = logging.getLogger(__name__)

try:
    import barcode
except ImportError:
    _logger.debug("Cannot import 'barcode' python Librairy.")
    barcode = None


class ResPartnerGenerateBarcodeWizard(models.TransientModel):
    _name = 'res.partner.generate.barcode.wizard'

    def _default_partner_id(self):
        return self.env.context.get('active_id', False)

    # Column Section
    partner_id = fields.Many2one(
        comodel_name='res.partner', default=_default_partner_id,
        required=True, readonly=True)

    current_barcode = fields.Char(
        related='partner_id.barcode', readonly=True)

    @api.multi
    def create_new_barcode(self):
        for wizard in self:
            barcode_rule = wizard.partner_id.barcode_rule_id

            padding = barcode_rule.pattern.count('N')
            begin = wizard.partner_id.barcode_rule_id.pattern.find('{')
            end = wizard.partner_id.barcode_rule_id.pattern.find('}') - 1

            # We assume that the pattern {NN} is at the end of the
            # pattern of the barcode rule
            custom_code = wizard.current_barcode[:begin]\
                + str(int(wizard.current_barcode[begin:end]) + 1).rjust(
                    padding, '0')

            barcode_class = barcode.get_barcode_class(barcode_rule.encoding)
            wizard.partner_id.barcode = barcode_class(custom_code)
