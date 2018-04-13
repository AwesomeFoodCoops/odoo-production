# -*- coding: utf-8 -*-

from openerp import api, models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.multi
    def unmatch_bankstatement(self):
        for record in self:
            if record.statement_line_id:
                for line in record.line_ids:
                    if line.statement_id.line_ids and record.statement_line_id\
                            in line.statement_id.line_ids:
                        line.write({'statement_id': False})
                record.write({
                    'statement_line_id': False
                })
        return True
