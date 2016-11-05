# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class CapitalFundraisingWizard(models.TransientModel):
    _inherit = 'capital.fundraising.wizard'

    def default_can_change_fundraising_category(self):
        return self.user_has_groups(
            'louve_membership.subscriptions_can_change_fundraising_category')

    def default_payment_term_id(self):
        return self.env.ref('account.account_payment_term_immediate').id

    def default_category_id(self):
        categories = self.env['capital.fundraising.category'].search(
            [('is_default', '=', True)])
        return categories and categories[0].id or False

    # Column Section
    payment_journal_id = fields.Many2one(required=True)

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', default=default_payment_term_id)

    category_id = fields.Many2one(
        comodel_name='capital.fundraising.category',
        default=default_category_id)

    can_change_fundraising_category = fields.Boolean(
        string="Can Change fundraising Category",
        default=default_can_change_fundraising_category)

    # Action Section
    @api.multi
    def button_confirm(self):
        barcode_rule_obj = self.env['barcode.rule']
        res = super(CapitalFundraisingWizard, self).button_confirm()
        wizard = self[0]
        if (wizard.category_id.is_part_A and
                not wizard.partner_id.barcode_rule_id and
                not wizard.partner_id.barcode_base):
            # Add the barcode rule
            barcode_rule_id = barcode_rule_obj.search(
                [('for_type_A_capital_subscriptor', '=', True)], limit=1)
            if barcode_rule_id:
                wizard.partner_id.barcode_rule_id = barcode_rule_id.id
                wizard.partner_id.generate_base()
                wizard.partner_id.generate_barcode()
        return res
