# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class CapitalFundraisingWizard(models.TransientModel):
    _inherit = 'capital.fundraising.wizard'

    def default_can_change_fundraising_category(self):
        return self.user_has_groups(
            'coop_membership.subscriptions_can_change_fundraising_category')

    def default_payment_term_id(self):
        return self.env.ref('account.account_payment_term_immediate').id

    def default_category_id(self):
        categories = self.env['capital.fundraising.category'].search(
            [('is_default', '=', True)])
        return categories and categories[0].id or False

    # Column Section
    can_change_fundraising_category = fields.Boolean(
        string="Can Change fundraising Category",
        default=default_can_change_fundraising_category)

    payment_journal_id = fields.Many2one(required=True)

    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term', default=default_payment_term_id)

    category_id = fields.Many2one(
        comodel_name='capital.fundraising.category',
        default=default_category_id)
    keep_partner_barcode = fields.Boolean(
        default=True,
        string="Keep existing barcode on Partner")

    # Action Section
    @api.multi
    def button_confirm(self):
        self.ensure_one()
        if (
            self.category_id.is_worker_capital_category
        ):
            if self.partner_id.is_associated_people:
                # If the partner is currently associated, make him cooperator
                self.partner_id.parent_id = False
                if not self.keep_partner_barcode:
                    self.partner_id.barcode_rule_id = False
            if not self.keep_partner_barcode:
                # Remove number
                self.partner_id.barcode_base = False
                self.partner_id.barcode = False
        res = super().button_confirm()
        # Add the barcode rule
        # We do it after calling super so that the sequence is assigned
        # at the very last moment, hence avoiding consuming numbers in
        # case of exception.
        if (
            self.category_id.is_worker_capital_category
            and not self.partner_id.barcode
            and (not self.keep_partner_barcode or self.partner_id.is_member or \
                self.partner_id.is_associated_people)
        ):
            if not self.partner_id.barcode_rule_id:
                barcode_rule_id = self.env['barcode.rule'].search(
                    [('for_type_A_capital_subscriptor', '=', True)], limit=1)
                if barcode_rule_id and barcode_rule_id.generate_type == 'sequence':
                    self.partner_id.barcode_rule_id = barcode_rule_id.id
            if self.partner_id.barcode_rule_id:
                self.partner_id.generate_base()
                self.partner_id.generate_barcode()
        return res
