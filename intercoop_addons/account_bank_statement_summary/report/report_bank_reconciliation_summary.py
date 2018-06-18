# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


from datetime import datetime
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.api import Environment
from openerp import SUPERUSER_ID
from openerp import _
import pytz
FORMAT_BOLD = '00'
FORMAT_NORMAL = '01'
FORMAT_RIGHT = '02'


class ReportBankReconciliationSummary(ReportXlsx):

    def create_xlsx_report(self, ids, data, report):
        self.env = Environment(self.env.cr, SUPERUSER_ID, self.env.context)
        return super(
            ReportBankReconciliationSummary, self
        ).create_xlsx_report(ids, data, report)

    def generate_xlsx_report(self, workbook, data, objects):
        self.object = objects[0]
        self._define_formats(workbook)
        self.sheet = workbook.add_worksheet()
        self.setup_config()
        # generate main content
        self.generate_report_title()
        # generate data table
        move_lines, bank_statement_lines, bank_balance, account_balance = self.get_data(self.object)
        self.generate_title_bank_reconciliation()
        total_move_line, total_debit_bank_statement_line = \
            self.generate_data_bank_reconciliation(
                move_lines, bank_statement_lines)
        self.load_data_blance(account_balance, bank_balance)

    def get_data(self, obj):
        journal_id = obj.journal_id and obj.journal_id.id or False
        default_account_credit = obj.journal_id and \
            obj.journal_id.default_credit_account_id and \
            obj.journal_id.default_credit_account_id.id or False
        bank_statement_lines = self.env['account.bank.statement.line'].search([
            ('date', '<=', obj.analysis_date),
            ('journal_id', '=', journal_id),
            ('journal_entry_ids', '=', False),
            ('statement_id.account_id', '=', default_account_credit)],
            order='date')

        # Get total debit bank statement line unmatch
        total_debit_sql = """SELECT sum(amount)
            FROM account_bank_statement_line
            WHERE date <= '%s' AND journal_id = %s
        """  % (obj.analysis_date, journal_id)
        self.env.cr.execute(total_debit_sql)
        bank_balance = self.env.cr.fetchone()
        bank_balance = bank_balance and bank_balance[0] or 0


        sql_move_lines = """SELECT ml.date, am.name, rp.name, ml.ref,
        ml.name, ml.debit, ml.credit
            FROM account_move_line ml
                LEFT JOIN account_move am ON ml.move_id = am.id
                LEFT JOIN res_partner rp ON ml.partner_id = rp.id
            WHERE ml.date <= '%s' AND ml.reconciled = false AND
            ml.statement_id is null AND
            ml.account_id = %s AND
            am.state = 'posted'
            ORDER BY ml.date""" % (obj.analysis_date, default_account_credit)
        self.env.cr.execute(sql_move_lines)
        move_lines = self.env.cr.fetchall()

        # Get total move line unreconciled, unmatched
        sql_move_lines_extend = """SELECT sum(ml.credit - ml.debit)
            FROM account_move_line ml
                LEFT JOIN account_move am ON ml.move_id = am.id
            WHERE ml.date <= '%s' AND
            ml.account_id = %s AND
            am.state = 'posted'
            """ % (obj.analysis_date, default_account_credit)
        self.env.cr.execute(sql_move_lines_extend)
        account_balance = self.env.cr.fetchone()
        account_balance = account_balance and account_balance[0] or 0


        return move_lines, bank_statement_lines, bank_balance, account_balance

    def _define_formats(self, workbook):
        # ---------------------------------------------------------------------
        # Common
        # ---------------------------------------------------------------------
        format_config = {
            'font_name': 'Calibri',
            'font_size': 11,
            'valign': 'vcenter',
            'text_wrap': True,
        }
        self.format_default = workbook.add_format(format_config)

        format_bold = format_config.copy()
        format_bold.update({
            'bold': True,
        })
        self.format_bold = workbook.add_format(format_bold)

        format_bold_balance = format_bold.copy()
        format_bold_balance.update({
            'align': 'right',
        })
        self.format_bold_balance = workbook.add_format(format_bold_balance)
        self.format_bold_balance.set_num_format('#,##0.00')

        format_bold_center = format_bold.copy()
        format_bold_center.update({
            'align': 'center',
        })
        self.format_bold_center = workbook.add_format(format_bold_center)

        format_right = format_config.copy()
        format_right.update({
            'align': 'right',
        })
        self.format_right = workbook.add_format(format_right)

        format_center = format_config.copy()
        format_center.update({
            'align': 'center',
        })
        self.format_center = workbook.add_format(format_center)

        # ---------------------------------------------------------------------
        # Report Template
        # ---------------------------------------------------------------------
        format_template_title = format_config.copy()
        format_template_title.update({
            'bold': True,
            'align': 'center',
        })
        self.format_template_title = workbook.add_format(format_template_title)

        # ---------------------------------------------------------------------
        # Report Title
        # ---------------------------------------------------------------------
        format_report_title = format_config.copy()
        format_report_title.update({
            'bold': True,
            'align': 'center',
            'font_size': 24,
        })
        self.format_report_title = workbook.add_format(format_report_title)

        format_uom = format_config.copy()
        format_uom.update({
            'italic': True,
            'align': 'right',
        })
        self.format_uom = workbook.add_format(format_uom)
        # ---------------------------------------------------------------------
        # Table format
        # ---------------------------------------------------------------------
        format_table = format_config.copy()
        format_table.update({
            'bold': True,
            'align': 'vcenter',
            'font_size': 14,
        })
        self.format_table = workbook.add_format(format_table)
        self.format_table.set_bg_color('#3399FF')
        self.format_table.set_font_color('#ffffff')

        format_table_date = format_config.copy()
        format_table_date.update({
            'border': True,
            'align': 'vcenter',
            'num_format': 'dd/mm/yyyy',
            'font_size': 11
        })
        self.format_table_date = workbook.add_format(format_table_date)
        self.format_table_date.set_bg_color('#3399FF')
        self.format_table_date.set_font_color('#ffffff')

        format_table_date_default = format_config.copy()
        format_table_date_default.update({
            'align': 'vcenter',
            'num_format': 'dd/mm/yyyy',
            'font_size': 11
        })
        self.format_table_date_default = workbook.add_format(
            format_table_date_default)

        format_table_center = format_table.copy()
        format_table_center.update({
            'border': True,
            'align': 'vcenter',
            'font_size': 11,
        })
        self.format_table_center = workbook.add_format(format_table_center)
        self.format_table_center.set_bg_color('#3399FF')
        self.format_table_center.set_font_color('#ffffff')

        format_table_bold = format_table.copy()
        format_table_bold.update({
            'bold': False,
            'font_size': 11,
            'align': 'vcenter',
        })
        self.format_table_bold = workbook.add_format(format_table_bold)

        format_table_bold_total = format_table.copy()
        format_table_bold_total.update({
            'font_size': 11,
            'align': 'right',
        })
        self.format_table_bold_total = workbook.add_format(
            format_table_bold_total)
        self.format_table_bold_total.set_bg_color('#808080')

        format_table_bold_total_number = format_table.copy()
        format_table_bold_total_number.update({
            'font_size': 11,
            'align': 'vcenter',
        })
        self.format_table_bold_total_number = workbook.add_format(
            format_table_bold_total_number)
        self.format_table_bold_total_number.set_font_color('#f90606')
        self.format_table_bold_total_number.set_num_format('#,##0.00')

        format_table_bold_total_number_balance = format_table.copy()
        format_table_bold_total_number_balance.update({
            'font_size': 11,
            'align': 'right',
        })
        self.format_table_bold_total_number_balance = workbook.add_format(
            format_table_bold_total_number_balance)
        self.format_table_bold_total_number_balance.set_font_color('#f90606')
        self.format_table_bold_total_number_balance.set_num_format('#,##0.00')

        format_table_number_bold = format_table.copy()
        format_table_number_bold.update({
            'bold': False,
            'font_size': 11,
            'align': 'vcenter',
        })
        self.format_table_number_bold = workbook.add_format(
            format_table_number_bold)
        self.format_table_number_bold.set_num_format('#,##0.00')

    def setup_config(self):
        self.row_pos = 0
        self.account_data = {}
        self._set_default_format()

    def _set_default_format(self):
        self.sheet.set_column('A:Z', None, self.format_default)
        self.sheet.set_row(4, 20)

        self.sheet.set_column('A:A', 15)
        self.sheet.set_column('B:B', 40)
        self.sheet.set_column('C:C', 40)
        self.sheet.set_column('D:D', 80)
        self.sheet.set_column('E:E', 60)
        self.sheet.set_column('F:F', 20)
        self.sheet.set_column('G:G', 20)

    def generate_report_title(self):
        self.sheet.merge_range(
            'A3:G4',
            _(u'Bank Reconciliation Summary'),
            self.format_report_title)

        self.sheet.write(
            "A8",
            _(u"Report Date"),
            self.format_bold
        )
        self.sheet.write(
            "A9",
            _(u"Printed by"),
            self.format_bold
        )
        self.sheet.write(
            "A10",
            _(u"Printed Date"),
            self.format_bold
        )
        self.sheet.write(
            "E8",
            _("Account "),
            self.format_bold
        )
        self.sheet.write(
            "E9",
            _(u"Currency"),
            self.format_bold
        )
        self.sheet.write(
            "C13",
            _(u"Account Balance"),
            self.format_bold
        )
        self.sheet.write(
            "C14",
            _(u"Bank Balance"),
            self.format_bold
        )
        self.sheet.write(
            "C15",
            _(u"Control"),
            self.format_bold
        )
        format_date = datetime.strptime(self.object.analysis_date, '%Y-%m-%d')
        analysis_date = format_date.strftime("%d/%m/%Y")
        self.sheet.write(
            "B8",
            u"%s" % analysis_date,
            self.format_table_date_default
        )

        self.sheet.write(
            "B9",
            u"%s" % self.object.create_uid.name or '',
            self.format_table_bold
        )

        self.sheet.write(
            "B10",
            u"%s" % pytz.utc.localize(datetime.now(), is_dst=False).astimezone(
                pytz.timezone(self.object.create_uid.tz)).strftime("%d/%m/%Y %H:%M:%S") or '',
            self.format_table_date_default
        )

        self.sheet.write(
            "F8",
            u"%s" % self.object.journal_id.name or '',
            self.format_table_bold
        )
        currency_id = self.object.journal_id.currency_id or \
            self.object.journal_id.company_id and \
            self.object.journal_id.company_id.currency_id or False
        self.sheet.write(
            "F9",
            u"%s" % currency_id and currency_id.name or '',
            self.format_table_bold
        )

    def generate_title_bank_reconciliation(self):
        self.sheet.merge_range(
            'A18:G18',
            _(u'Outstanding Journal Items'),
            self.format_table)
        self.sheet.write(
            "A19",
            _(u"Date"),
            self.format_table_date
        )
        self.sheet.write(
            "B19",
            _(u"Journal Entry"),
            self.format_table_center
        )
        self.sheet.write(
            "C19",
            _(u"Partner"),
            self.format_table_center
        )
        self.sheet.write(
            "D19",
            _(u"Partner Reference"),
            self.format_table_center
        )
        self.sheet.write(
            "E19",
            _(u"Label"),
            self.format_table_center
        )
        self.sheet.write(
            "F19",
            _(u"Debit"),
            self.format_table_center
        )
        self.sheet.write(
            "G19",
            _(u"Credit"),
            self.format_table_center
        )

    def generate_outstanding_bank(self, row):
        self.sheet.merge_range(
            'A%s:G%s' % (row, row),
            _(u'Outstanding Bank Transactions'),
            self.format_table)
        self.sheet.write(
            "A%s" % (row + 1),
            _(u"Date"),
            self.format_table_date
        )
        self.sheet.write(
            "B%s" % (row + 1),
            _(u"Reference"),
            self.format_table_center
        )
        self.sheet.write(
            "C%s" % (row + 1),
            _(u"Partner"),
            self.format_table_center
        )
        self.sheet.write(
            "D%s" % (row + 1),
            _(u"Memo"),
            self.format_table_center
        )
        self.sheet.write(
            "E%s" % (row + 1),
            u"",
            self.format_table_center
        )
        self.sheet.write(
            "F%s" % (row + 1),
            _(u"Debit"),
            self.format_table_center
        )
        self.sheet.write(
            "G%s" % (row + 1),
            _(u"Credit"),
            self.format_table_center
        )

    def generate_data_bank_reconciliation(
            self, move_lines, bank_statement_lines):
        row = 20
        total_debit_bank_statement_line = 0
        total_credit_move_line = 0
        total_debit_move_line = 0
        total_move_line = 0
        for move_line in move_lines:
            format_date = datetime.strptime(
                move_line[0], '%Y-%m-%d')
            move_line_date = format_date.strftime("%d/%m/%Y")
            self.sheet.write(
                "A%s" % row,
                u"%s" % move_line_date,
                self.format_table_date_default)
            self.sheet.write(
                "B%s" % row,
                u"%s" % move_line[1] or '',
                self.format_table_bold)
            partner = '' if move_line[2] is None else move_line[2]
            self.sheet.write(
                "C%s" % row,
                u"%s" % partner,
                self.format_table_bold)
            reference = '' if move_line[3] is None else move_line[3]
            self.sheet.write(
                "D%s" % row,
                u"%s" % reference,
                self.format_table_bold)
            Label = '' if move_line[4] is None else move_line[4]
            self.sheet.write(
                "E%s" % row,
                u"%s" % Label,
                self.format_table_bold)
            self.sheet.write_number(
                "F%s" % row,
                float(move_line[5]) or 0.00,
                self.format_table_number_bold)
            self.sheet.write_number(
                "G%s" % row,
                float(move_line[6]) or 0.00,
                self.format_table_number_bold)
            total_debit_move_line += move_line[5]
            total_credit_move_line += move_line[6]
            row += 1
        total_move_line = total_credit_move_line - total_debit_move_line
        self.sheet.merge_range(
            'A%s:E%s' % (row, row),
            _(u'Total Journal Items'),
            self.format_table_bold_total)
        if total_credit_move_line >= total_debit_move_line:
            self.sheet.write_number(
                "G%s" % row,
                float(total_move_line),
                self.format_table_bold_total_number)
        else:
            self.sheet.write_number(
                "F%s" % row,
                float(total_move_line),
                self.format_table_bold_total_number)
        row += 5
        self.generate_outstanding_bank(row)
        row += 2
        for bank_statement_line in bank_statement_lines:
            bank_debit = 0.0
            bank_credit = 0.0
            if bank_statement_line.amount < 0:
                bank_debit = bank_statement_line.amount
            else:
                bank_credit = bank_statement_line.amount
            format_date = datetime.strptime(
                bank_statement_line.date, '%Y-%m-%d')
            bank_statement_line_date = format_date.strftime("%d/%m/%Y")
            self.sheet.write(
                "A%s" % row,
                u"%s" % bank_statement_line_date,
                self.format_table_date_default)
            ref = '' if not bank_statement_line.ref else \
                bank_statement_line.ref
            self.sheet.write(
                "B%s" % row,
                u"%s" % ref,
                self.format_table_bold)
            self.sheet.write(
                "C%s" % row,
                u"%s" % bank_statement_line.partner_id and
                bank_statement_line.partner_id.name or '',
                self.format_table_bold)
            self.sheet.write(
                "D%s" % row,
                u"%s" % bank_statement_line.name or '',
                self.format_table_bold)
            self.sheet.write(
                "E%s" % row,
                u"%s" % '',
                self.format_table_bold)
            self.sheet.write_number(
                "F%s" % row,
                float(bank_debit),
                self.format_table_number_bold)
            self.sheet.write(
                "G%s" % row,
                float(bank_credit),
                self.format_table_number_bold)
            total_debit_bank_statement_line += bank_statement_line.amount
            row += 1
        self.sheet.merge_range(
            'A%s:E%s' % (row, row),
            _(u'Total Bank Transactions'),
            self.format_table_bold_total)
        if total_debit_bank_statement_line >= 0:
            self.sheet.write_number(
                "G%s" % row,
                float(total_debit_bank_statement_line),
                self.format_table_bold_total_number)
        else:
            self.sheet.write_number(
                "F%s" % row,
                float(total_debit_bank_statement_line),
                self.format_table_bold_total_number)
        return total_move_line, total_debit_bank_statement_line

    def load_data_blance(
            self, total_move_line, total_debit_bank_statement_line):
        self.sheet.write_number(
            "D13",
            float(total_move_line),
            self.format_bold_balance)
        self.sheet.write_number(
            "D14",
            float(total_debit_bank_statement_line),
            self.format_bold_balance)
        self.sheet.write_number(
            "D15",
            float((total_move_line + total_debit_bank_statement_line)),
            self.format_table_bold_total_number_balance)


ReportBankReconciliationSummary(
    'report.bank_reconciliation_summary_xlsx',
    'bank.reconciliation.summary.wizard')
