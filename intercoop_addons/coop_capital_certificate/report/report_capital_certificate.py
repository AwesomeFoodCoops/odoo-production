# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from datetime import date


class CapitalCertificateReport(models.Model):
    _name = "report.coop_capital_certificate.report_capital_certificate"

    @api.multi
    def render_html(self, data):
        certificate_id = self.id
        docs = self.env['capital.certificate'].browse(certificate_id)
        docargs = {
            'doc_ids': certificate_id,
            'partner_id': self.env.user.partner_id,
            'doc_model': 'capital.certificate',
            'docs': docs,
            'date': date,
        }
        return self.env['report'].render(
            'coop_capital_certificate.capital_certificate_report_template',
            docargs)
