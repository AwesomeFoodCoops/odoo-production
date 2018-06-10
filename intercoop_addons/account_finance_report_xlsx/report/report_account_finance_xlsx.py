# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html


from datetime import datetime
from openerp.osv.fields import datetime as datetime_field
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.api import Environment
from openerp import SUPERUSER_ID
from openerp import _, models
import pytz
FORMAT_BOLD = '00'
FORMAT_NORMAL = '01'
FORMAT_RIGHT = '02'


class ReportAccountFinancial(ReportXlsx):

    def create_xlsx_report(self, ids, data, report):
        self.context = data['context']
        self.env = Environment(self.env.cr, SUPERUSER_ID, self.env.context)
        return super(ReportAccountFinancial,
                     self).create_xlsx_report(ids, data, report)

    def generate_xlsx_report(self, workbook, data, objects):
        self.object = objects[0]
        ReportFinancial = self.env['report.account.report_financial']
        get_account_lines = ReportFinancial.get_account_lines(data.get('form'))
        self._define_formats(workbook)
        self.sheet = workbook.add_worksheet()
        self.setup_config()
        # generate report titile

        # data is data[form]
        data = data['form']

        self.generate_report_title(data)
        self.generate_info_general_report(data, get_account_lines, workbook)

        # template 1
        if not data['enable_filter'] and not data['debit_credit']:
            self.template_for_not_filter_not_debit_credit(
                data, get_account_lines, workbook)
        elif data['debit_credit'] == 1:
            self.template_for_not_filter_debit_credit(
                data, get_account_lines, workbook)
        elif data['enable_filter'] == 1 and not data['debit_credit']:
            self.template_for_filter_not_debit_credit(
                data, get_account_lines, workbook)

    def generate_info_general_report(self, data, get_account_lines, workbook):
        self.sheet.write(
            "A5",
            _(u"Target Moves:"),
            self.format_title_table
        )
        if data['target_move'] == 'all':
            self.sheet.write(
                "A6",
                _(u"All Entries"),
                self.format_default_info
            )
        elif data['target_move'] == 'posted':
            self.sheet.write(
                "A6",
                _(u"All Posted Entries"),
                self.format_default_info
            )
        if data['date_from']:
            self.sheet.write(
                "B5",
                _(u"Date from:"),
                self.format_title_table
            )
            self.sheet.write(
                "B6",
                u"%s" % data['date_from'],
                self.format_default_info
            )
        if data['date_to']:
            self.sheet.write(
                "C5",
                _(u"Date to:"),
                self.format_title_table
            )
            self.sheet.write(
                "C6",
                u"%s" % data['date_to'],
                self.format_default_info
            )
        self.sheet.write(
            "D5",
            _(u"Print Date:"),
            self.format_title_table
        )
        self.sheet.write(
            "D6",
            u"%s" % datetime_field.context_timestamp(self.env.cr, self.env.uid, datetime.now(
            ), self.context).strftime("%d/%m/%Y %H:%M") or '',
            self.format_default_info
        )

    def template_for_not_filter_not_debit_credit(self, data, get_account_lines, workbook):
        '''
        Prepare template for data like qweb format: ==>

        <table class="table table-condensed" t-if="not data['enable_filter'] and not data['debit_credit']">
            <thead>
                <tr>
                    <th>Name</th>
                    <th class="text-right">Balance</th>
                </tr>
            </thead>
            <tbody>
                <tr t-foreach="get_account_lines" t-as="a">
                    <t t-if="a['level'] != 0">
                        <t t-if="a.get('level') &gt; 3"><t t-set="style" t-value="'font-weight: normal;'"/></t>
                        <t t-if="not a.get('level') &gt; 3"><t t-set="style" t-value="'font-weight: bold;'"/></t>

                        <td>
                            <span style="color: white;" t-esc="'..' * a.get('level', 0)"/>
                            <span t-att-style="style" t-esc="a.get('name')"/>
                        </td>
                        <td class="text-right"><span t-att-style="style" t-esc="a.get('balance')" t-esc-options='{"widget": "monetary", "display_currency": "res_company.currency_id"}'/></td>
                    </t>
                </tr>
            </tbody>
        </table>
        '''

        self.sheet.write(
            "A8",
            _(u"Name"),
            self.format_title_table
        )
        self.sheet.write(
            "B8",
            _(u"Balance"),
            self.format_title_table
        )
        row = 9
        for line in get_account_lines:
            cell_style = self.format_default
            balance_style = self.format_right_balance
            row_level = line.get('level', 0)
            if row_level != 0:
                if not row_level > 3:
                    cell_style = self.format_bold
                    balance_style = self.format_bold_balance
                self.sheet.write(
                    "A%s" % row,
                    u"%s%s" % ("    " * row_level, line['name']) or '',
                    cell_style)
                self.sheet.write(
                    "B%s" % row,
                    float(line['balance']) or 0,
                    balance_style)
                row += 1

    def template_for_not_filter_debit_credit(self, data, get_account_lines, workbook):
        '''
        Prepare template for data like qweb format: ==>

        <table class="table table-condensed" t-if="data['debit_credit'] == 1">
            <thead>
                <tr>
                    <th>Name</th>
                    <th class="text-right">Debit</th>
                    <th class="text-right">Credit</th>
                    <th class="text-right">Balance</th>
                </tr>
            </thead>
            <tbody>
                <tr t-foreach="get_account_lines" t-as="a">
                    <t t-if="a['level'] != 0">
                        <t t-if="a.get('level') &gt; 3"><t t-set="style" t-value="'font-weight: normal;'"/></t>
                        <t t-if="not a.get('level') &gt; 3"><t t-set="style" t-value="'font-weight: bold;'"/></t>

                        <td>
                            <span style="color: white;" t-esc="'..' * a.get('level', 0)"/>
                            <span t-att-style="style" t-esc="a.get('name')"/>
                        </td>
                        <td class="text-right" style="white-space: text-nowrap;">
                            <span t-att-style="style" t-esc="a.get('debit')" t-esc-options='{"widget": "monetary", "display_currency": "res_company.currency_id"}'/>
                        </td>
                        <td class="text-right" style="white-space: text-nowrap;">
                            <span t-att-style="style" t-esc="a.get('credit')" t-esc-options='{"widget": "monetary", "display_currency": "res_company.currency_id"}'/>
                        </td>
                        <td class="text-right" style="white-space: text-nowrap;">
                            <span t-att-style="style" t-esc="a.get('balance')" t-esc-options='{"widget": "monetary", "display_currency": "res_company.currency_id"}'/>
                        </td>
                    </t>
                </tr>
            </tbody>
        </table>
        '''

        self.sheet.write(
            "A8",
            _(u"Name"),
            self.format_title_table
        )
        self.sheet.write(
            "B8",
            _(u"Debit"),
            self.format_title_table
        )
        self.sheet.write(
            "C8",
            _(u"Credit"),
            self.format_title_table
        )
        self.sheet.write(
            "D8",
            _(u"Balance"),
            self.format_title_table
        )
        row = 9
        for line in get_account_lines:
            cell_style = self.format_default
            balance_style = self.format_right_balance
            row_level = line.get('level', 0)
            if row_level != 0:
                if not row_level > 3:
                    cell_style = self.format_bold
                    balance_style = self.format_bold_balance

                self.sheet.write(
                    "A%s" % row,
                    u"%s%s" % ("    " * row_level, line['name']) or '',
                    cell_style)
                self.sheet.write(
                    "B%s" % row,
                    float(line['debit']) or 0,
                    balance_style)
                self.sheet.write(
                    "C%s" % row,
                    float(line['credit']) or 0,
                    balance_style)
                self.sheet.write(
                    "D%s" % row,
                    float(line['balance']) or 0,
                    balance_style)
                row += 1

    def template_for_filter_not_debit_credit(self, data, get_account_lines, workbook):
        '''
        Prepare template for data like qweb format: ==>

        <table class="table table-condensed" t-if="data['enable_filter'] == 1 and not data['debit_credit']">
            <thead>
                <tr>
                    <th>Name</th>
                    <th class="text-right">Balance</th>
                    <th class="text-right"><span t-esc="data['label_filter']"/></th>
                </tr>
            </thead>
            <tbody>
                <tr t-foreach="get_account_lines" t-as="a">
                    <t t-if="a['level'] != 0">
                        <t t-if="a.get('level') &gt; 3"><t t-set="style" t-value="'font-weight: normal;'"/></t>
                        <t t-if="not a.get('level') &gt; 3"><t t-set="style" t-value="'font-weight: bold;'"/></t>
                        <td>
                            <span style="color: white;" t-esc="'..'"/>
                            <span t-att-style="style" t-esc="a.get('name')"/>
                        </td>
                        <td class="text-right"><span t-att-style="style" t-esc="a.get('balance')" t-esc-options='{"widget": "monetary", "display_currency": "res_company.currency_id"}'/></td>
                        <td class="text-right"><span t-att-style="style" t-esc="a.get('balance_cmp')"/></td>
                    </t>
                </tr>
            </tbody>
        </table>
        '''

        self.sheet.write(
            "A8",
            _(u"Name"),
            self.format_title_table
        )
        self.sheet.write(
            "B8",
            _(u"Balance"),
            self.format_title_table
        )
        self.sheet.write(
            "C8",
            u"%s" % data['label_filter'],
            self.format_title_table
        )
        row = 9
        for line in get_account_lines:
            cell_style = self.format_default
            balance_style = self.format_right_balance
            row_level = line.get('level', 0)
            if row_level != 0:
                if not row_level > 3:
                    cell_style = self.format_bold
                    balance_style = self.format_bold_balance

                self.sheet.write(
                    "A%s" % row,
                    u"%s%s" % ("    " * row_level, line['name']) or '',
                    cell_style)
                self.sheet.write(
                    "B%s" % row,
                    float(line['balance']) or 0,
                    balance_style)
                self.sheet.write(
                    "C%s" % row,
                    float(line['balance_cmp']) or 0,
                    balance_style)
                row += 1

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

        format_right_balance = format_right.copy()
        self.format_right_balance = workbook.add_format(format_right_balance)
        self.format_right_balance.set_num_format('#,##0.00')

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

        format_title_table = format_config.copy()
        format_title_table.update({
            'bold': True,
            'align': 'center',
        })
        self.format_title_table = workbook.add_format(format_title_table)

        format_default_info = format_config.copy()
        format_default_info.update({
            'align': 'center'
        })
        self.format_default_info = workbook.add_format(format_default_info)

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
        self._set_default_format()

    def _set_default_format(self):
        self.sheet.set_column('A:Z', None, self.format_default)

        self.sheet.set_column('A:A', 70)
        self.sheet.set_column('B:B', 20)
        self.sheet.set_column('C:C', 20)
        self.sheet.set_column('D:D', 20)

    def generate_report_title(self, data):
        self.sheet.merge_range(
            'A3:G4',
            _(u'%s' % data['account_report_id'][1]),
            self.format_report_title)


ReportAccountFinancial(
    'report.report_account_financial_xlsx',
    'account.financial.report',
)
