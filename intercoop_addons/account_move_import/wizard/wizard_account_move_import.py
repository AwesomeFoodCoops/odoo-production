# -*- coding: utf-8 -*-
from xlrd import open_workbook
import base64
from datetime import datetime

from openerp import models, fields, api, _


JOURNALS = [
    ('ACMR', 'ACH'),
    ('BNK1', 'CM'),
    ('NDF', 'NDF'),
    ('OD', 'OD'),
    ('VTE1', 'VTE')
]


class AccountMoveImport(models.TransientModel):
    _name = 'account.move.import'
    _description = 'Import Account Moves import'

    file = fields.Binary('File', required=True)
    journal = fields.Selection(JOURNALS, 'Journal', required=True)
    filename = fields.Char('Filename')

    @api.one
    def start_import(self):
        start_date = datetime.now()
        wb = open_workbook(file_contents=base64.decodestring(self.file))
        items = []
        header_name = []
        header_row_number = 0
        for sheet in wb.sheets():
            for column in range(sheet.ncols):
                line = sheet.cell(header_row_number, column).value
                header_name.append(line)
            # Reading lines
            for row in range(sheet.nrows):
                if row == 0:
                    continue
                value = {}
                i = 0
                for column in range(sheet.ncols):
                    line = sheet.cell(row, column).value
                    if line:
                        value[header_name[i]] = line
                    # Create all
                    i += 1
                items.append(value)
        move_lines = []
        created = 0
        partner = False
        for item in items:
            if len(move_lines) == 0 and item.get('Li'):
                journal = self.env['account.journal'].search([
                    ('code', '=', self.journal)
                ])

                move_dict = {
                    'date': datetime.strptime(item['Dte'], '%d/%m/%Y').date(),
                    'ref': item[u'Référence'] if u'référence' in item else '',
                    'journal_id': journal.id,
                    'partner_id': partner.id if partner else False,
                }

            if not item.get('Li'):
                if len(move_lines) > 0:
                    move_dict.update({
                        'line_ids': move_lines
                    })
                    move_id = self.env['account.move'].create(move_dict)
                    move_id.post()
                    created += 1
                    move_lines = []
                    partner = False
                continue
            account_id = self.env['account.account'].search([
                ('code', '=', item['Compte'])
            ])
            if not partner and item.get('Auxiliaire'):
                partner = self.env['res.partner'].search([
                    '|',
                    ('display_name', 'ilike', item['Auxiliaire']),
                    ('ref', '=', item['Auxiliaire'])
                ])
            move_lines.append((0, 0, {
                'account_id': account_id.id,
                'name': item[u'Libellé'],
                'debit': item[u'Débit'] if item.get(u'Débit') else 0.0,
                'credit': item[u'Crédit'] if item.get(u'Crédit') else 0.0,
                'partner_id': partner.id if partner else False,
            }))

        # Create the import history
        self.env['account.move.import.history'].create({
            'name': _('Import of {} journal'.format(self.journal)),
            'created_moves': created,
            'date': start_date,
            'filename': self.filename
        })
        return True
