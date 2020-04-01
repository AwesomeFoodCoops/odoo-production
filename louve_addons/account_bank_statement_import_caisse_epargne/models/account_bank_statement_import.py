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

    regexp_version = {
        'version_A' : {
            'line_1' : u"^Code de la banque : (?P<bank_group_code>\d{5});Code de l'agence : (?P<bank_local_code>\d{5});Date de début de téléchargement : (?P<opening_date>\d{2}/\d{2}/\d{4});Date de fin de téléchargement : (?P<closing_date>\d{2}/\d{2}/\d{4});;$",
            'line_2' : u"^Numéro de compte : (?P<bank_account_number>\d{11});Nom du compte : (?P<bank_account_name>.*);Devise : (?P<currency>.{3});;;$",
            'line_closing_balance' : u"^Solde en fin de période;;;;(?P<balance>\d+(,\d{1,2})?);$",
            'line_opening_balance' : u"^Solde en début de période;;;;(?P<balance>\d+(,\d{1,2})?);$",
            'line_credit' : u"^(?P<date>\d{2}/\d{2}/\d{4});(?P<unique_import_id>.*);(?P<name>.*);;(?P<credit>\d+(,\d{1,2})?);(?P<note>.*)$",
            'line_debit' : u"^(?P<date>\d{2}/\d{2}/\d{4});(?P<unique_import_id>.*);(?P<name>.*);(?P<debit>-\d+(,\d{1,2})?);;(?P<note>.*)$",
        },
        'version_B' : {
            'line_1' : u"^Code de la banque : (?P<bank_group_code>\d{5});Date de début de téléchargement : (?P<opening_date>\d{2}/\d{2}/\d{4});Date de fin de téléchargement : (?P<closing_date>\d{2}/\d{2}/\d{4});;$",
            'line_2' : u"^Numéro de compte : (?P<bank_account_number>\d{11});Devise : (?P<currency>.{3});;;$",
            'line_closing_balance' : u"^Solde en fin de période;;;(?P<balance>\d+(,\d{1,2})?);$",
            'line_opening_balance' : u"^Solde en début de période;;;(?P<balance>\d+(,\d{1,2})?);$",
            'line_credit' : u"^(?P<date>\d{2}/\d{2}/\d{4});(?P<name>.*);;(?P<credit>\d+(,\d{1,2})?);(?P<note>.*)$",
            'line_debit' : u"^(?P<date>\d{2}/\d{2}/\d{4});(?P<name>.*);(?P<debit>-\d+(,\d{1,2})?);;(?P<note>.*)$",
            }
    }
    @api.model
    def _check_file(self, data_file):
        try:
            file_version = "version_A"
            #for files generated before june 2017
            test_version = re.compile(u"^Code de la banque : (?P<bank_group_code>\d{5});Code de l'agence : (?P<bank_local_code>\d{5});Date de début de téléchargement : (?P<opening_date>\d{2}/\d{2}/\d{4});Date de fin de téléchargement : (?P<closing_date>\d{2}/\d{2}/\d{4});;$").search(data_file[0])
            if (test_version == None):
                #for files generated after june 2017
                file_version = "version_B"

            parse_line_1 = re.compile(self.regexp_version[file_version]['line_1']).search(data_file[0])
            _logger.error("========================================="+file_version)
            bank_group_code = parse_line_1.group('bank_group_code')
            _logger.error("========================================= A")
            openning_date = parse_line_1.group('opening_date')
            _logger.error("========================================= B")
            closing_date = parse_line_1.group('closing_date')
            _logger.error("========================================= C")

            parse_line_2 = re.compile(self.regexp_version[file_version]['line_2']).search(data_file[1])
            bank_account_number = parse_line_2.group('bank_account_number')
            _logger.error("========================================= D")
            currency = parse_line_2.group('currency')
            _logger.error("========================================= E")

            closing_balance = float(re.compile(self.regexp_version[file_version]['line_closing_balance']).search(data_file[3]).group('balance').replace(',','.'))
            _logger.error("========================================= F")
            opening_balance = float(re.compile(self.regexp_version[file_version]['line_opening_balance']).search(data_file[len(data_file)-1]).group('balance').replace(',','.'))
            _logger.error("========================================= G")

        except Exception as e:
            _logger.debug(e)
            return False
        return (file_version,bank_group_code,openning_date,closing_date,bank_account_number,opening_balance,closing_balance,currency)

    @api.model
    def _parse_file(self, data_file):
        data_file = data_file.splitlines()
        result = self._check_file(data_file)
        if not result:
            return super(AccountBankStatementImport, self)._parse_file(
                data_file)

        file_version,bank_group_code,openning_date,closing_date,bank_account_number,opening_balance,closing_balance,currency = result
        transactions = []
        total_amt = 0.00
        try:
            index = 0
            for line in data_file[5:len(data_file)-1]:
                transaction = re.compile(self.regexp_version[file_version]['line_debit']).search(line)
                if (transaction != None):
                    transaction_amount = float(transaction.group('debit').replace(',','.'))
                else :
                    transaction = re.compile(self.regexp_version[file_version]['line_credit']).search(line)
                    transaction_amount = float(transaction.group('credit').replace(',','.'))

                vals_line = {
                    'date': datetime.datetime.strptime(transaction.group('date'), '%d/%m/%Y').strftime('%Y-%m-%d'),
                    'name': transaction.group('name'),
                    #'ref': transaction.group('unique_import_id'),
                    'amount': transaction_amount,
                    'note': transaction.group('note'),
                    'unique_import_id': str(index)+transaction.group('date')+transaction.group('name')+str(transaction_amount)+transaction.group('note'),
                    'account_number': bank_account_number,
                }
                total_amt += transaction_amount
                transactions.append(vals_line)
                index = index + 1

            if (abs(opening_balance+total_amt-closing_balance) > 0.00001):
                raise ValueError(_("Sum of opening balance and transaction lines is not equel to closing balance."))

        except Exception as e:
            raise Warning(_("The following problem occurred during import. The file might not be valid.\n\n %s" % e.message))

        vals_bank_statement = {
            'name': bank_account_number+"/"+openning_date,
            'date': datetime.datetime.strptime(openning_date, '%d/%m/%Y').strftime('%Y-%m-%d'),
            'transactions': list(reversed(transactions)),
            'balance_start': opening_balance,
            'balance_end_real': closing_balance,
        }
        return currency, bank_account_number, [vals_bank_statement]
