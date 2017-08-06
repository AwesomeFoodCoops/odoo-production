# -*- coding: utf-8 -*-

import logging
import StringIO
import re
import datetime

from openerp import api, models
from openerp.tools.translate import _
from openerp.exceptions import Warning

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _inherit = 'account.bank.statement.import'

    @api.model
    def _check_file(self, data_file):
        try:
            parse_line_1 = re.compile(u"^Code de la banque : (?P<bank_group_code>\d{5});Code de l'agence : (?P<bank_local_code>\d{5});Date de début de téléchargement : (?P<opening_date>\d{2}/\d{2}/\d{4});Date de fin de téléchargement : (?P<closing_date>\d{2}/\d{2}/\d{4});;$").search(data_file[0])
            bank_group_code = parse_line_1.group('bank_group_code')
            bank_local_code = parse_line_1.group('bank_local_code')
            openning_date = parse_line_1.group('opening_date')
            closing_date = parse_line_1.group('closing_date')

            parse_line_2 = re.compile(u"^Numéro de compte : (?P<bank_account_number>\d{11});Nom du compte : (?P<bank_account_name>.*);Devise : (?P<currency>.{3});;;$").search(data_file[1])
            bank_account_number = parse_line_2.group('bank_account_number')
            bank_account_name = parse_line_2.group('bank_account_name')
            currency = parse_line_2.group('currency')

            closing_balance = float(re.compile(u"^Solde en fin de période;;;;(?P<balance>\d+(,\d{1,2})?);$").search(data_file[3]).group('balance').replace(',','.'))
            opening_balance = float(re.compile(u"^Solde en début de période;;;;(?P<balance>\d+(,\d{1,2})?);$").search(data_file[len(data_file)-1]).group('balance').replace(',','.'))

        except Exception as e:
            _logger.debug(e)
            return False
        return (bank_group_code,bank_local_code,openning_date,closing_date,bank_account_number,bank_account_name,opening_balance,closing_balance,currency)

    @api.model
    def _parse_file(self, data_file):
        data_file = data_file.splitlines()
        result = self._check_file(data_file)
        if not result:
            return super(AccountBankStatementImport, self)._parse_file(
                data_file)

        bank_group_code,bank_local_code,openning_date,closing_date,bank_account_number,bank_account_name,opening_balance,closing_balance,currency = result
        transactions = []
        total_amt = 0.00
        try:
            for line in data_file[5:len(data_file)-1]:
#                _logger.debug(line)
                transaction = re.compile(u"^(?P<date>\d{2}/\d{2}/\d{4});(?P<unique_import_id>.*);(?P<name>.*);(?P<debit>-\d+(,\d{1,2})?);;(?P<note>.*)$").search(line)
                if (transaction != None):
                    transaction_amount = float(transaction.group('debit').replace(',','.'))
                else :
                    transaction = re.compile(u"^(?P<date>\d{2}/\d{2}/\d{4});(?P<unique_import_id>.*);(?P<name>.*);;(?P<credit>\d+(,\d{1,2})?);(?P<note>.*)$").search(line)
                    transaction_amount = float(transaction.group('credit').replace(',','.'))

                #bank_account_id = partner_id = False
                #banks = self.env['res.partner.bank'].search(
                #    [('bank_name', '=', transaction.payee)], limit=1)
                #if banks:
                #    bank_account = banks[0]
                #    bank_account_id = bank_account.id
                #    partner_id = bank_account.partner_id.id

                vals_line = {
                    'date': datetime.datetime.strptime(transaction.group('date'), '%d/%m/%Y').strftime('%Y-%m-%d'),
                    'name': transaction.group('name'),
                    'ref': transaction.group('unique_import_id'),
                    'amount': transaction_amount,
                    'note': transaction.group('note'),
                    'unique_import_id': transaction.group('unique_import_id'),
                    'account_number': bank_account_number,
                    #'bank_account_id': bank_account_id,
                }
                total_amt += transaction_amount
                transactions.append(vals_line)

            if (abs(opening_balance+total_amt-closing_balance) > 0.00001):
                raise ValueError(_("Sum of opening balance and transaction lines is not equel to closing balance."))

        except Exception,e:
            raise Warning(_("The following problem occurred during import. The file might not be valid.\n\n %s" % e.message))

        vals_bank_statement = {
            'name': bank_account_number+"/"+openning_date,
            'date': datetime.datetime.strptime(openning_date, '%d/%m/%Y').strftime('%Y-%m-%d'),
            'transactions': list(reversed(transactions)),
            'balance_start': opening_balance,
            'balance_end_real': closing_balance,
        }
        return currency, bank_account_number, [vals_bank_statement]
