# -*- coding: utf-8 -*-
# Copyright (C) 2019 Druidoo <https://www.druidoo.io>

from openerp import api, models, fields, _


class PosSession(models.Model):
    _inherit = 'pos.session'

    @api.multi
    def check_cash_in_out_possible(self):
        self.ensure_one()
        if not self.cash_register_id:
            raise UserError(_(
                "There's no cash register on this session"))
        if not self.cash_register_id.journal_id:
            raise UserError(_(
                "Please check that the field 'Journal' is set "
                "on the Bank Statement"))
        if not self.cash_register_id.journal_id.company_id.transfer_account_id:
            raise UserError(_(
                "Please check that the field 'Transfer Account' is set "
                "on the company."))
        if self.cash_register_id.state == 'confirm':
            raise UserError(_(
                "You cannot put/take money in/out for a bank statement "
                "which is closed."))
        return True

    @api.multi
    def action_put_money_in(self, amount, reason):
        self.ensure_one()
        wizard = self.env['cash.box.in'].create({
            'amount': amount, 'name': reason})
        wizard.with_context(active_model=self._name, active_ids=self.ids).run()

    @api.multi
    def action_take_money_out(self, amount, reason):
        self.ensure_one()
        wizard = self.env['cash.box.out'].create({
            'amount': amount, 'name': reason})
        wizard.with_context(active_model=self._name, active_ids=self.ids).run()
