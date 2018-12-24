# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models

class ReportPrintbadge(models.AbstractModel):
    _name = 'report.coop_print_badge.report_printbadge'

    @api.multi
    def render_html(self, data):
        res_partner_env = self.env['res.partner']
        partners = res_partner_env.search([('id', 'in', self.ids)])
        images = {}
        for partner in partners:
            partner.untick_badges_to_print()
            partner.update_badge_print_date()
            images[partner.id] = partner.image_medium

        docargs = {
            'doc_ids': self.ids,
            'partner_id': self.env.user.partner_id,
            'doc_model': 'res.partner',
            'partners': partners,
            'images': images,
        }
        return self.env['report'].render(
            'coop_print_badge.report_printbadge', docargs)
