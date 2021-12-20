# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class MergePartnerAutomatic(models.TransientModel):
    _inherit = 'base.partner.merge.automatic.wizard'

    @api.model
    def _update_values(self, src_partners, dst_partner):
        super(MergePartnerAutomatic, self)._update_values(
            src_partners, dst_partner)
        dst_partner._compute_total_partner_owned_share()
        dst_partner._compute_is_worker_member()
        dst_partner._compute_number_of_associated_people()
        dst_partner._compute_is_unsubscribed()
        dst_partner._compute_is_underclass_population()
        dst_partner._compute_is_former_associated_people()
        dst_partner._compute_cooperative_state()

    @api.model
    def update_for_already_merged(self):
        sql = """
        SELECT DISTINCT rp.id
        FROM res_partner_owned_share s
        JOIN res_partner rp ON rp.id = s.partner_id
        WHERE rp.is_member ISNULL 
            OR rp.is_member IS FALSE
        ORDER BY rp.id
        """
        self.env.cr.execute(sql)
        datas = self.env.cr.fetchall()
        partner_ids = [d[0] for d in datas]
        if partner_ids:
            partners = self.env['res.partner'].browse(partner_ids)
            partners._compute_total_partner_owned_share()
            partners._compute_is_worker_member()
            partners._compute_number_of_associated_people()
            partners._compute_is_unsubscribed()
            partners._compute_is_underclass_population()
            partners._compute_is_former_associated_people()
            partners._compute_cooperative_state()
