# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


FUNDRAISING_CATEGORIES = [
    'is_part_A',
    'is_part_B',
    'is_part_C',
]


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def generate_certificate(self, year=False):
        if not year:
            return False

        aml_obj = self.env['account.move.line']
        cc_obj = self.env['capital.certificate']
        mail_template = self.env.ref(
            "coop_capital_certificate.capital_certificate_mail_template")
        min_date = "%s-01-01" % (year)
        max_date = "%s-01-01" % (year + 1)

        config = self.env['account.config.settings'].search([])[0]
        account_ids = config.capital_account_ids
        if not account_ids:
            raise UserError(_(
                """Please define the Capital Partner accounts in the """
                """Accounting / Configuration / Configuration menu."""))
        account_list = [account.id for account in account_ids]

        for partner in self:
            lines = []
            aml_ids = aml_obj.search([
                ('partner_id', '=', partner.id),
                ('date', '>=', min_date),
                ('date', '<', max_date),
                ('account_id', 'in', account_list),
                ('debit', '>', 0),
            ], order='account_id')
            for aml in aml_ids:
                amount = 0
                price = aml.product_id.list_price
                qty = aml.debit / price
                credit_moves = sorted(
                    aml.matched_credit_ids,
                    key=lambda m: m.credit_move_id.date, reverse=True)
                payment_date = credit_moves and\
                    credit_moves[0].credit_move_id.date or fields.Date.today()
                if not aml.reconciled:
                    amount = credit_moves and\
                        sum([cm.credit for cm in credit_moves]) or 0
                lines.append({
                    'date': aml.date,
                    'qty': qty,
                    'category': aml.account_id.name[-1:],
                    'price': price,
                    'payment_date': payment_date,
                    'reconciled': aml.reconciled,
                    'amount': amount,
                })

            lines = map(lambda x: (0, 0, x), lines)
            cc = cc_obj.create({
                'partner_id': partner.id,
                'year': year,
                'template_id': mail_template.id,
                'line_ids': lines,
            })
            cc.execute()
