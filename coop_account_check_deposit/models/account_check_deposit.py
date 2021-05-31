from odoo import models, fields, api


class AccountCheckDeposit(models.Model):
    _inherit = "account.check.deposit"

    name = fields.Char(copy=False)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    check_holder_name = fields.Char(string="Cheque Holder")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        change_check_holder_name = self._context.get(
            'change_check_holder_name', False)
        if self.partner_id and not self.check_holder_name:
            if change_check_holder_name or self.check_deposit_id:
                self.check_holder_name = self.partner_id.name_get()[0][1] or ''

    @api.model
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        res.update_check_holder_name()
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        self.update_check_holder_name()
        return res

    @api.multi
    def update_check_holder_name(self):
        '''
            Update check holder name for item was generate from deposit
        '''
        for record in self:
            if record.check_deposit_id and record.partner_id and not\
                    record.check_holder_name:
                record.check_holder_name = record.partner_id.name_get()[
                    0][1] or ''
            elif not record.check_deposit_id and record.check_holder_name:
                record.check_holder_name = ""
