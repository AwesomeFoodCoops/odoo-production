# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import UserError


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

        cfc_obj = self.env['capital.fundraising.category']
        account_list = tuple(
            [c.capital_account_id.id for c in cfc_obj.search([])])
        for partner in self:
            lines = []
            aml_ids = aml_obj.search([
                ('partner_id', '=', partner.id),
                ('date', '>=', min_date),
                ('date', '<', max_date),
                ('account_id', 'in', account_list),
                ('credit', '>', 0),
            ], order='account_id')
            for aml in aml_ids:
                price = aml.product_id.list_price
                qty = aml.credit / price
                lines.append({
                    'date': aml.invoice_id.date_invoice,
                    'qty': qty,
                    'product': aml.product_id.name,
                    'price': price,
                    'payment_date': aml.date,
                })

            lines = map(lambda x: (0, 0, x), lines)
            cc = cc_obj.create({
                'partner_id': partner.id,
                'year': year,
                'template_id': mail_template.id,
                'line_ids': lines,
            })
            cc.execute()
