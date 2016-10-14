# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fundraising_partner_type_ids = fields.Many2many(
        comodel_name='capital.fundraising.partner.type',
        string='Fundraising Partner Type')
    has_capital_subscription = fields.Boolean(
        'Has a capital subscription',
        compute="compute_has_capital_subscription")

    @api.multi
    def compute_has_capital_subscription(self):
        for partner in self:
            invoice_obj = self.env['account.invoice']
            line_ids = invoice_obj.search([
                ('partner_id', '=', partner.id),
                ('state', 'in', ('open', 'paid'))]).mapped(
                'invoice_line_ids').filtered(
                lambda l: l.product_id.is_capital_fundraising)
            partner.has_capital_subscription = len(line_ids)
