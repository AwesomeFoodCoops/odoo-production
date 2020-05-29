# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
from odoo.tools.safe_eval import safe_eval


class PosConfig(models.Model):
    _inherit = "pos.config"

    diacritics_insensitive_search = fields.Boolean(
        default=False,
        compute="_compute_diacritics_insensitive_search",
        inverse="_set_diacritics_insensitive_search",
        string="Diacritics insensitive search",
    )

    account_journal_ids = fields.Many2many(
        "account.journal",
        "rel_pos_config_journal",
        "rel_account_journal_pos",
        string="Cheques Journals",
        help="Please indicate here the cheques journals for which you "
        + "would like to display a message when used in POS",
    )

    payable_to = fields.Char(string="Payable to")

    @api.model
    def default_get(self, fields):
        res = super(PosConfig, self).default_get(fields)
        journal_ids = self.env.user.company_id.journal_config_ids
        payable_to = self.env.user.company_id.payable_to
        res.update(
            {
                "account_journal_ids": [(6, 0, journal_ids.ids)],
                "payable_to": payable_to,
            }
        )
        return res

    @api.multi
    def execute(self):
        for record in self:
            self.env.user.company_id.journal_config_ids = [
                (6, 0, record.account_journal_ids.ids)
            ]
            self.env.user.company_id.payable_to = record.payable_to

        return super(PosConfig, self).execute()

    @api.multi
    def _set_diacritics_insensitive_search(self):
        ir_config_env = self.env["ir.config_parameter"]
        for rec in self:
            ir_config_env.sudo().set_param(
                "diacritics_insensitive_search",
                rec.diacritics_insensitive_search
            )

    @api.multi
    def _compute_diacritics_insensitive_search(self):
        ir_config_env = self.env["ir.config_parameter"]
        value = safe_eval(
            ir_config_env.sudo().get_param("diacritics_insensitive_search", "False")
        )
        for record in self:
            record.diacritics_insensitive_search = value
