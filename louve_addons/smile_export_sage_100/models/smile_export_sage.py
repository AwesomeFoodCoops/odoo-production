# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2014 Smile (<http://www.smile.fr>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, api, models, exceptions, _
import base64
from openerp.tools import ustr
from datetime import datetime, date
import unicodedata


def convert_to_sage_date_format(date):
    """Converts a date to Sage date format: JJMMAA

    @date: date
    @return: str
    """
    year = datetime.strptime(str(date), "%Y-%m-%d").strftime('%y')
    month = datetime.strptime(str(date), "%Y-%m-%d").strftime('%m')
    day = datetime.strptime(str(date), "%Y-%m-%d").strftime('%d')
    return "%s%s%s" % (day, month, year)


def dict_to_list(keys, dic):
    """Build a list from values of a dictionary and ordered by the list of keys.
        dict_to_list(['b', 'a'], {'a': 1', 'b': 2}) returns [2, 1]

    @keys: list
    @dic: dict
    @return: list
    """
    res = []
    for key in keys:
        res.append(dic[key])
    return res


def strip_accents(s):
    """Replace accent in a string by non accentued letters.

    @s: unicode
    @return: unicode
    """
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    exported = fields.Boolean('Exported', default=False)


class SmileExportSage(models.Model):
    _name = "smile.export.sage"

    name = fields.Char('Export filename', size=32, required=True, translate=True, default=lambda self: self._get_default_name())
    extension = fields.Selection([('txt', 'Txt')], 'Extension', default='txt')
    state = fields.Selection([('draft', 'Draft'), ('exported', 'Exported')], 'State', default='draft')
    last_export_date = fields.Date(string='Last Export Date', compute='_get_last_export_date', readonly=True, help='Last date of export')
    # Options
    filter_move_lines = fields.Selection([('all', 'Export all move lines'), ('non_exported', 'Export only non exported move lines')],
                                         'Move lines to export', default='non_exported')
    # Filters
    date_from = fields.Date('From date')
    date_to = fields.Date('To date')
    invoice_ids = fields.Many2many('account.invoice', string='Invoice')
    journal_ids = fields.Many2many('account.journal', string='Account Journals')
    move_ids = fields.Many2many('account.move', string='Move')
    partner_ids = fields.Many2many('res.partner', string='Partner')

    @api.one
    def _get_last_export_date(self):
        ir_attachment_ids = self.env["ir.attachment"].search([('res_model', '=', 'smile.export.sage'), ('res_id', '=', self.id)])
        if ir_attachment_ids:
            ir_attachment_ids.sorted(key=lambda v: v.write_date)
        self.last_export_date = ir_attachment_ids and ir_attachment_ids[-1].write_date or False

    @api.model
    def _get_default_name(self):
        return "export%s" % date.today().strftime("%y%m%d")

    @api.multi
    def _get_move_line_search_domain(self):
        """Returns the search domain for move lines in this export.

        @return: list
        """
        self.ensure_one()
        res = []
        # Exclusion of unposted move lines
        res.append(('move_id.state', '!=', 'draft'))
        # Options
        if self.filter_move_lines == 'non_exported':
            res.append(('exported', '=', False))
        # Filters
        if self.date_from:
            res.append(('date', '>=', self.date_from))
        if self.date_to:
            res.append(('date', '<=', self.date_to))
        if self.invoice_ids:
            res.append(('invoice', 'in', self.invoice_ids.ids))
        if self.journal_ids:
            res.append(('journal_id', 'in', self.journal_ids.ids))
        if self.move_ids:
            res.append(('move_id', 'in', self.move_ids.ids))
        if self.partner_ids:
            res.append(('partner_id', 'in', self.partner_ids.ids))

        return res

    @api.model
    def _get_unbalanced_moves(self):
        unbalanced_move_lines = self.env["account.move.line"].search([('state', '=', 'draft')])
        return [str(move_line.move_id.id) for move_line in unbalanced_move_lines]

    @api.multi
    def create_report(self):
        """Creates documents export for Sage 100.

        @return: str
        """
        self.ensure_one()
        self.UNASSIGNED_JOURNAL_SAGE_CODES = []
        self.UNASSIGNED_ACCOUNT_SAGE_CODES = []
        # The order of the list elements is important. Sage 100 uses the order of the elements of the imported file.
        self.MOVE_LINE_KEYS = ['marker', 'journal_code', 'move_line_date', 'export_date', 'account_move_name', 'invoice_number',
                               'treasury_piece', 'general_account', 'compensation_general_account', 'partner_account',
                               'compensation_partner_account', 'title', 'payment_number', 'maturity_date', 'parity', 'quantity',
                               'currency_number', 'sense', 'amount', 'total_letter_number', 'currency_letter_number', 'counting_number',
                               'reminder_count', 'deferral_method_type', 'revision_type', 'currency_amount', 'tax_code']
        self.LINE_SEPARATOR = '\r\n'

        move_line_obj = self.env["account.move.line"]
        # Get move lines to export
        domain = self._get_move_line_search_domain()
        move_line_ids = move_line_obj.search(domain)
        if not move_line_ids:
            raise exceptions.Warning(_("There are no move lines to export."))
        datas = self._get_datas(move_line_ids)

        # Create a document with output as content
        vals = {
            'name': "%s.%s" % (self.name, self.extension),
            'type': 'binary',
            'datas': base64.encodestring(ustr(datas)),
            'datas_fname': "%s.%s" % (self.name, self.extension),
            'res_model': 'smile.export.sage',
            'res_id': self.id,
        }
        self.env["ir.attachment"].create(vals)

        # Change report state to exported
        self.state = 'exported'

        # Prepare warning about unbalanced moves and unassigned Sage account and journal codes
        message = ''
        unbalanced_moves = self._get_unbalanced_moves()
        if unbalanced_moves:
            message += "Les pièces suivantes ne sont pas équilibrées: {}.".format(', '.join(set(unbalanced_moves)))
        if self.UNASSIGNED_JOURNAL_SAGE_CODES:
            message += \
                "\n\nAucun journal Sage n'a été défini pour ces journaux: {}.".format(', '.join(set(self.UNASSIGNED_JOURNAL_SAGE_CODES)))
        if self.UNASSIGNED_ACCOUNT_SAGE_CODES:
            message += \
                "\n\nAucun compte Sage n'a été défini pour ces comptes: {}.".format(', '.join(set(self.UNASSIGNED_ACCOUNT_SAGE_CODES)))
        if message != '':
            raise exceptions.Warning(_(message))
        return True

    @api.multi
    def _get_datas(self, move_line_ids):
        """Get datas to export.

        @return: str
        """
        self.ensure_one()
        output = []
        # Content of the export
        output += self.build_header()
        for move_line_id in move_line_ids:
            output += self.build_account_move_line(move_line_id)
        output += self.build_footer()
        datas = self.LINE_SEPARATOR.join(output)
        # Marks move lines as exported
        move_line_ids.write({'exported': True})
        return datas

    @api.multi
    def _get_account_move_name(self, move_line):
        """Returns the move name required by Sage 100 import.

        @move_line: the move line whom the move name is searched
        @return: str
        """
        self.ensure_one()
        return move_line.move_id and move_line.move_id.name and ustr(move_line.move_id.name)

    @api.multi
    def _get_invoice_number(self, move_line):
        """Returns the invoice number required by Sage 100 import.

        @move_line: the move line whom the invoice number is searched
        @return: str
        """
        self.ensure_one()
        return move_line.invoice_id and move_line.invoice_id.number

    @api.multi
    def _get_general_account(self, move_line):
        """Returns the general account required by Sage 100 import.

        @move_line: the move line whom the general account is searched
        @return: str
        """
        self.ensure_one()
        general_account = ''
        account_code = move_line.account_id and move_line.account_id.code
        if account_code:
            # The context MUST be passed to get the Sage codes related to this partner in the right company.
            # context['company_id'] = invoice and invoice.company_id and invoice.company_id.id
            # partner = invoice and invoice.partner_id and self.pool.get('res.partner').browse(cr, uid, invoice.partner_id.id, context)
            partner = move_line.invoice_id and move_line.invoice_id.partner_id
            if partner and account_code[:3] == '401':
                if partner.property_account_payable_sage:
                    general_account = partner.property_account_payable_sage
                else:
                    general_account = account_code
                    self.UNASSIGNED_ACCOUNT_SAGE_CODES.append("(%s, %s %s)" % (partner.name, account_code, move_line.account_id.name))
            elif partner and account_code[:3] == '411':
                if partner.property_account_receivable_sage:
                    general_account = partner.property_account_receivable_sage
                else:
                    general_account = account_code
                    self.UNASSIGNED_ACCOUNT_SAGE_CODES.append("(%s, %s %s)" % (partner.name, account_code, move_line.account_id.name))
            else:
                general_account = "%s000" % account_code
        return general_account

    @api.multi
    def _get_partner_account(self, move_line):
        """Returns the partner account required by Sage 100 import.

        @move_line: the move line whom the partner account is searched
        @return: str
        """
        self.ensure_one()
        partner_account = move_line.partner_id and move_line.partner_id.property_account_receivable_sage
        return partner_account[3:] if partner_account else ''

    @api.multi
    def _get_title(self, move_line):
        """Returns the title required by Sage 100 import.

        @move_line: the move line whom the title is searched
        @return: str
        """
        self.ensure_one()
        return move_line.name

    @api.model
    def build_header(self):
        """Returns the header of the file.

        @return: str list
        """
        args = []
        args.append('#FLG 000')
        args.append('#VER 5')
        args.append('#DEV EUR')
        return args

    @api.model
    def build_footer(self):
        """Returns the footer of the file.

        @return: str list
        """
        return ['#FIN']

    @api.multi
    def build_account_move_line(self, move_line):
        """Converts informations about an account move line to Sage format.
        See http://bit.ly/1n7ru0h at page 819 for more informations.

        @account_move_line_id: int, id of the move line to export
        @return: str list
        """
        self.ensure_one()
        move_line_values = {}
        if not move_line:
            # No move_line with this id
            return []
        # Get informations
        move_line_values['marker'] = '#MECG'
        # Journal code
        if move_line.journal_id:
            if move_line.journal_id.sage_code:
                journal_code = move_line.journal_id.sage_code
            else:
                journal_code = move_line.journal_id.code
                self.UNASSIGNED_JOURNAL_SAGE_CODES.append(move_line.journal_id.code)
        else:
            journal_code = ''
        move_line_values['journal_code'] = journal_code[:6]
        move_line_values['move_line_date'] = convert_to_sage_date_format(move_line.date) if move_line.date else ''
        move_line_values['export_date'] = convert_to_sage_date_format(date.today())
        account_move_name = self._get_account_move_name(move_line)
        move_line_values['account_move_name'] = account_move_name[:13] if account_move_name else ''
        invoice_number = self._get_invoice_number(move_line)
        move_line_values['invoice_number'] = invoice_number[:17] if invoice_number else ''
        move_line_values['treasury_piece'] = ''
        general_account = self._get_general_account(move_line)
        move_line_values['general_account'] = general_account[:13] if general_account else ''
        move_line_values['compensation_general_account'] = ''
        partner_account = self._get_partner_account(move_line)
        move_line_values['partner_account'] = partner_account[:17] if partner_account else ''
        move_line_values['compensation_partner_account'] = ''
        title = self._get_title(move_line)
        move_line_values['title'] = title[:35] if title else ''
        move_line_values['payment_number'] = '0'
        move_line_values['maturity_date'] = convert_to_sage_date_format(move_line.date_maturity) if move_line.date_maturity else ''
        move_line_values['parity'] = '0,000000'
        move_line_values['quantity'] = '0,00'
        move_line_values['currency_number'] = '0'
        if move_line.debit > 0:
            sense = '0'
            amount = ustr(move_line.debit)
        else:
            sense = '1'
            amount = ustr(move_line.credit)
        move_line_values['sense'] = sense
        move_line_values['amount'] = amount[:14]
        move_line_values['total_letter_number'] = ''
        move_line_values['currency_letter_number'] = ''
        move_line_values['counting_number'] = ''
        move_line_values['reminder_count'] = '0'
        move_line_values['deferral_method_type'] = '0'
        move_line_values['revision_type'] = '0'
        move_line_values['currency_amount'] = ''
        move_line_values['tax_code'] = '0'
        # following fields described in documentation are not yet treated

        # Strip accents to fix encoding problems
        for key in self.MOVE_LINE_KEYS:
            value = move_line_values[key]
            move_line_values[key] = strip_accents(value) if type(value) == unicode else value
        return dict_to_list(self.MOVE_LINE_KEYS, move_line_values)
