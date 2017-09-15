# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# @author: Julien Weste
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    fundraising_partner_type_ids = fields.Many2many(
        comodel_name='capital.fundraising.partner.type',
        string='Fundraising Partner Type')

    amount_subscription = fields.Float(
        string="Total Subscribed Amount",
        compute='compute_amount_subscription')

    # Compute section
    @api.multi
    def compute_amount_subscription(self):
        inv_obj = self.env['account.invoice']
        for partner in self:
            amount_subscription = sum(inv_obj.search([
                ('type', '=', 'out_invoice'),
                ('partner_id', '=', partner.id),
                ('is_capital_fundraising', '=', True),
                ('state', 'in', ['paid', 'open'])
            ]).mapped('amount_total_signed'))
            partner.amount_subscription = amount_subscription + sum(
                inv_obj.search([
                    ('type', '=', 'out_refund'),
                    ('partner_id', '=', partner.id),
                    ('is_capital_fundraising', '=', True),
                    ('state', 'in', ['paid', 'open'])
                ]).mapped('amount_total_signed'))
