# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountMoveImportHistory(models.Model):
    _name = 'account.move.import.history'
    _description = 'Hisotries of account moves imports'
    _order = 'date desc'

    name = fields.Char('Object')
    date = fields.Datetime('Date')
    created_moves = fields.Integer('Created Moves')
    filename = fields.Char('Imported file')
