# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class CapitalCertificateWizard(models.TransientModel):
    _name = "capital.certificate.wizard"
    _description = "Capital Fiscal Certificate Report"

    @api.model
    def _get_default_year(self):
        current_date = fields.Date.from_string(fields.Date.today())
        return current_date.year - 1

    year = fields.Integer(string="Year", default=_get_default_year)

    @api.multi
    def generate_certificates(self, data):
        self.ensure_one()

        query = """
            SELECT
                rp.id
            FROM
                res_partner as rp, account_invoice as ai,
            account_invoice_line as ail,
            product_product as pp, product_template as pt
            WHERE
                rp.id = ai.partner_id AND
                ail.invoice_id = ai.id AND ail.product_id = pp.id AND
                pp.product_tmpl_id = pt.id AND
                pt.is_capital_fundraising is true AND
                EXTRACT(YEAR FROM ai.date_invoice) = %s
            GROUP BY
                rp.id
        """

        year = self.read(['year'])[0]['year']
        params = tuple([str(year)])
        self.env.cr.execute(query, params)
        partner_ids = self.env.cr.fetchall()
        partner_ids = [p[0] for p in partner_ids]

        partners = self.env['res.partner'].browse(partner_ids)
        partners.generate_certificate(year)
