# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from openerp import models, fields, api


class PosConfigSettings(models.Model):
    _inherit = 'pos.config.settings'

    receipt_options = fields.Selection(
        [
            (1, 'Do not send receipt via email'),
            (2, 'Email receipt and print it'),
            (3, 'Email receipt and print it unless configured on user that he only receives electronically')
        ], string="Receipt"
    )

    @api.model
    def get_default_receipt_options(self, fields):
        receipt_options = self.env['ir.values'].get_default(
            'pos.config.settings', 'receipt_options')
        return {
            'receipt_options': receipt_options,
        }

    @api.multi
    def set_default_receipt_options(self):
        self.ensure_one()
        return self.env['ir.values'].sudo().set_default(
            'pos.config.settings', 'receipt_options',
            self.receipt_options or None)
