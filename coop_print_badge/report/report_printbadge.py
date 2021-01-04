# Copyright (C) 2017-Today: La Louve (<http://www.lalouve.net/>)
# @author: Julien Weste (julien.weste@akretion.com)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ReportPrintbadge(models.AbstractModel):
    _name = 'report.coop_print_badge.report_printbadge'
    _description = 'Report Coop Print Badge'

    @api.multi
    def _get_report_values(self, docids, data=None):
        res_partner_env = self.env['res.partner']
        partners = res_partner_env.browse(docids)
        for partner in partners:
            partner.untick_badges_to_print()
            partner.update_badge_print_date()
            # partner.image = partner.image_medium 
            if not partner.image_badge and partner.image:
                partner.image_badge = partner.image
        return {
            'doc_ids': docids,
            'doc_model': 'res.partner',
            'docs': partners,
            'data': data,
        }
