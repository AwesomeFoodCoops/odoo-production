# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Author Julien Weste - La Louve 2016
#    Inspired by Smile (smile_export_software_100)
#    and GRAP (account_export_ebp)
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
import cStringIO
from unidecode import unidecode
from openerp.tools import ustr
from datetime import datetime, date
import unicodedata


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
    return ''.join(c for c in unicodedata.normalize('NFD', s)
                   if unicodedata.category(c) != 'Mn')


class AccountExport(models.Model):
    _name = "account.export"

    name = fields.Char(
        'Export filename', size=32, required=True,
        default=lambda self: self._get_default_name())
    extension = fields.Selection([('csv', 'Csv')], 'Extension', default='csv')
    state = fields.Selection(
        [('draft', 'Draft'), ('exported', 'Exported')], 'State',
        default='draft')
    last_export_date = fields.Date(
        string='Last Export Date', compute='_get_last_export_date',
        readonly=True, help='Last date of export')
    # Options
    filter_move_lines = fields.Selection([
        ('all', 'Export all move lines'),
        ('non_exported', 'Export only non exported move lines')],
        'Move lines to export', default='non_exported')
    # Filters
    date_from = fields.Date('From date')
    date_to = fields.Date('To date')
    invoice_ids = fields.Many2many('account.invoice', string='Invoice')
    journal_ids = fields.Many2many(
        'account.journal', string='Account Journals')
    partner_ids = fields.Many2many('res.partner', string='Partner')
    config_id = fields.Many2one(
        string='Export Configuration', comodel_name='account.export.config',
        default=lambda self: self._get_default_config(), required=True)

    def convert_to_software_date_format(self, date):
        dateformat = self.config_id and self.config_id.dateformat or "%d%m%y"
        return datetime.strptime(str(date), "%Y-%m-%d").strftime(dateformat)

    @api.one
    def _get_last_export_date(self):
        ir_attachment_ids = self.env["ir.attachment"].search([
            ('res_model', '=', 'account.export'), ('res_id', '=', self.id)])
        if ir_attachment_ids:
            ir_attachment_ids.sorted(key=lambda v: v.write_date)
        self.last_export_date = ir_attachment_ids and\
            ir_attachment_ids[-1].write_date or False

    @api.model
    def _get_default_name(self):
        return "export%s" % date.today().strftime("%y%m%d")

    @api.model
    def _get_default_config(self):
        config = self.env['account.export.config'].search(
            [('is_default', '=', True)])
        if not config:
            config = self.env['account.export.config'].search()
        return config and config[0].id or False

    @api.multi
    def _get_move_search_domain(self):
        self.ensure_one()
        res = []
        res.append(('state', '!=', 'draft'))
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
        if self.partner_ids:
            res.append(('partner_id', 'in', self.partner_ids.ids))
        return res

    @api.model
    def _get_unbalanced_moves(self, move_ids):
        unbalanced_move_lines = move_ids.filtered(
            lambda m: m.state == 'draft')
        return [
            str(move.id) for move in unbalanced_move_lines]

    @api.multi
    def create_report(self):
        self.ensure_one()
        self.UNASSIGNED_JOURNAL_CODES = []
        self.UNASSIGNED_ACCOUNT_CODES = []
        self.MOVE_LINE_KEYS = [
            'journal_code', 'move_line_date', 'move_number', 'account',
            'aux', 'account_move_name', 'sense', 'amount', ]
        self.LINE_SEPARATOR = '\r\n'

        move_obj = self.env["account.move"]
        # Get move lines to export
        domain = self._get_move_search_domain()
        move_ids = move_obj.search(domain)
        if not move_ids:
            raise exceptions.Warning(_("There are no moves to export."))
        datas = self._get_datas(move_ids)

        moves_file = cStringIO.StringIO()
        for line in datas:
            moves_file.write(unidecode(line))
            moves_file.write(self.LINE_SEPARATOR)
        out_moves = base64.encodestring(moves_file.getvalue())
        moves_file.close()

        # Create a document with output as content
        vals = {
            'name': "%s.%s" % (self.name, self.extension),
            'type': 'binary',
            'datas': out_moves,
            'datas_fname': "%s.%s" % (self.name, self.extension),
            'res_model': 'account.export',
            'res_id': self.id,
        }
        self.env["ir.attachment"].create(vals)

        # Change report state to exported
        self.state = 'exported'

        # Prepare warning about unbalanced moves and unassigned accounts and
        # journal codes
        message = ''
        unbalanced_moves = self._get_unbalanced_moves(move_ids)
        if unbalanced_moves:
            message += "Les pièces suivantes ne sont pas équilibrées: {}."\
                .format(', '.join(set(unbalanced_moves)))
        if self.UNASSIGNED_JOURNAL_CODES:
            message += \
                "\n\nAucun code d'export n'est défini pour ces journaux: {}."\
                .format(', '.join(set(self.UNASSIGNED_JOURNAL_CODES)))
        if self.UNASSIGNED_ACCOUNT_CODES:
            message += \
                "\n\nAucun compte d'export n'est défini pour ces comptes: {}."\
                .format(', '.join(set(self.UNASSIGNED_ACCOUNT_CODES)))
        if message != '':
            raise exceptions.Warning(_(message))
        return True

    @api.multi
    def _get_datas(self, move_ids):
        self.ensure_one()
        output = []

        header = self.build_header()
        if header:
            output += [header]
        for move_id in move_ids:
            output += self.build_account_move(move_id)
        footer = self.build_footer()
        if footer:
            output += [footer]

        move_ids.write({'exported': True})
        return output

    @api.multi
    def _get_account_move_desc(self, move_lines):
        self.ensure_one()
        move_line = move_lines[0]
        if move_line.move_id.journal_id.type == "sale":
            desc = move_line.ref
        elif move_line.move_id.journal_id.type == "purchase":
            desc = move_line.move_id.partner_id.name
        else:
            desc = move_line.ref or '' + move_line.name or ''
        return desc

    @api.multi
    def _get_account(self, move_line):
        self.ensure_one()
        account = ''
        account_code = move_line.account_id and move_line.account_id.code
        if account_code:
            partner = move_line.invoice_id and move_line.invoice_id.partner_id
            if partner and account_code[:3] == '401':
                if partner.property_account_payable_software:
                    account = partner.property_account_payable_software
                else:
                    account = account_code
                    self.UNASSIGNED_ACCOUNT_CODES.append(
                        "(%s, %s %s)" % (
                            partner.name, account_code,
                            move_line.account_id.name))
            elif partner and account_code[:3] == '411':
                if partner.property_account_receivable_software:
                    account = partner.property_account_receivable_software
                else:
                    account = account_code
                    self.UNASSIGNED_ACCOUNT_CODES.append(
                        "(%s, %s %s)" % (
                            partner.name, account_code,
                            move_line.account_id.name))
            else:
                account = "%s000" % account_code
        return account

    @api.model
    def build_header(self):
        return self.config_id and self.config_id.header or False

    @api.model
    def build_footer(self):
        return self.config_id and self.config_id.footer or False

    @api.multi
    def build_account_move(self, move):
        self.ensure_one()

        move_values = []
        group_fields = move.journal_id.group_fields
        exported_lines = []
        for line in move.line_ids:
            if line.id in exported_lines:
                continue

            if group_fields:
                lines = move.line_ids.filtered(
                    lambda l: l.id not in exported_lines and
                    all([l[field.name] == line[field.name]
                        for field in group_fields]))
            else:
                lines = line

            move_values += [self.build_account_move_line(lines, group_fields)]
            exported_lines += [li.id for li in lines]
        return move_values

    @api.multi
    def build_account_move_line(self, move_lines, group_fields=False):
        self.ensure_one()
        move_line_values = {}
        move_line = move_lines[0]

        if move_line.journal_id:
            if move_line.journal_id.export_code:
                journal_code = move_line.journal_id.export_code
            else:
                journal_code = move_line.journal_id.code
                self.UNASSIGNED_JOURNAL_CODES.append(move_line.journal_id.code)
        else:
            journal_code = ''
        move_line_values['journal_code'] = journal_code[:6]

        move_line_values['move_line_date'] =\
            self.convert_to_software_date_format(
                max([line.date for line in move_lines])) or ''

        move_line_values['move_number'] = move_line.move_id.name

        account = self._get_account(move_line)
        move_line_values['account'] = account[:13] if account else ''

        move_line_values['aux'] = move_line.move_id.partner_id.barcode or 'EE'

        account_move_name = self._get_account_move_desc(move_lines)
        move_line_values['account_move_name'] = account_move_name[:13]\
            if account_move_name else ''

        debit = sum(line.debit for line in move_lines)
        credit = sum(line.credit for line in move_lines)
        if debit - credit > 0:
            sense = '0'
            amount = ustr(debit - credit)
        else:
            sense = '1'
            amount = ustr(credit - debit)
        move_line_values['sense'] = sense
        move_line_values['amount'] = amount[:14]

        for key in move_line_values.keys():
            value = move_line_values[key]
            move_line_values[key] = strip_accents(move_line_values[key])\
                if type(value) == unicode else value
        move_line_list = dict_to_list(self.MOVE_LINE_KEYS, move_line_values)
        return ",".join(move_line_list)
