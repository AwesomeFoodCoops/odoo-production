# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


from openerp import models, fields, api


class UnmatchBankStatementWizard(models.TransientModel):
    _name = 'unmatch.bank.statement.wizard'
    _description = 'Unmatch Bank Statement Wizard'

    mess_confirm = fields.Text(string="Message Confirm")

    @api.multi
    def unmatch_bankstatement(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids', [])
        active_model = self._context.get('active_model', [])

        if active_model == 'account.move':
            moves = self.env['account.move'].browse(active_ids)
            moves.unmatch_bankstatement()
        elif active_model == 'account.move.line':
            moves =\
                self.env['account.move.line'].browse(
                    active_ids).mapped('move_id')
            moves.unmatch_bankstatement()
        return True
