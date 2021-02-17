# -*- coding: utf-8 -*-

from collections import OrderedDict
from xlsxwriter.utility import xl_rowcol_to_cell

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.api import Environment
from openerp import SUPERUSER_ID
from openerp import fields, _


class ReportStockInventoryXlsx(ReportXlsx):

    def create_xlsx_report(self, ids, data, report):
        self.env = Environment(self.env.cr, SUPERUSER_ID, self.env.context)
        return super(ReportStockInventoryXlsx,
                     self).create_xlsx_report(ids, data, report)

    def generate_xlsx_report(self, workbook, data, objects):
        self.object = objects[0]
        self._define_formats(workbook)
        self.sheet = workbook.add_worksheet()
        self.setup_config()

        self.generate_report_title()
        self.generate_report_general(data)
        self.row_pos += 2
        
        history_values_lst = data.get('history_values_lst', [])
        self.generate_table_header()
        self.write_history_data(history_values_lst)

    def setup_config(self):
        self.row_pos = 5
        self._set_default_format()
        self.info_labels = {
            'internal_ref': {
                'str': u"Référence",
                'index': 1
            },
            'barcode': {
                'str': 'Code barre',
                'index': 2
            },
            'name': {
                'str': 'Article',
                'index': 3
            },
            'quantity': {
                'str': u'Quantité',
                'format': self.format_table_number,
                'index': 4
            },
            'standard_price': {
                'str': u"Coût",
                'format': self.format_table_number,
                'index': 5
            },
            'value': {
                'str': u'Valeur',
                'type': 'formula',
                'format': self.format_table_number,
                'index': 6,
            }
        }
        # Get list of column key ordered by index
        self.columns = OrderedDict(
            sorted(self.info_labels.items(), key=lambda (k, v): v['index'])
        ).keys()

    def _set_default_format(self):
        self.sheet.set_default_row(20)
        self.sheet.set_column('A:Z', None, self.format_default)
        self.sheet.set_column('A:A', 30)
        self.sheet.set_column('B:B', 20)
        self.sheet.set_column('C:C', 50)
        self.sheet.set_column('D:F', 20)

    def generate_report_general(self, data):
        row_pos = self.row_pos
        col_pos = 0
        print_date_str = data.get('print_date', '')
        created_at_header = u'Créé le : '
        self.sheet.write_rich_string(
            row_pos, col_pos,
            self.format_bold, created_at_header,
            self.format_default, print_date_str
        )
        row_pos += 1

        created_uid = self.object._context.get('uid', self.env.uid)
        created_user = self.env['res.users'].browse(created_uid)
        created_by_header = u'Créé par : '
        self.sheet.write_rich_string(
            row_pos, col_pos,
            self.format_bold, created_by_header,
            self.format_default, created_user.name
        )

        row_pos += 1
        inventory_date_str = data.get('inventory_date', '')
        inventory_at_header = u'Inventaire au : '
        self.sheet.write_rich_string(
            row_pos, col_pos,
            self.format_bold, inventory_at_header,
            self.format_default, inventory_date_str
        )
        row_pos += 1
        self.row_pos = row_pos

    def generate_report_title(self):
        self.sheet.merge_range(
            'B2:F5',
            u'Inventaire à date',
            self.format_report_title)

    def generate_table_header(self):
        row_pos = self.row_pos
        cell_format = self.format_table_header
        for col_pos, column in enumerate(self.columns):
            label_str = self.info_labels.get(column, {}).get('str', '')
            self.sheet.write(row_pos, col_pos, label_str, cell_format)

        row_pos += 1
        self.row_pos = row_pos

    def write_history_data(self, history_values_lst):
        row_pos = self.row_pos
        start_row_pos = row_pos
        stop_row_pos = row_pos
        length = len(history_values_lst)
        is_summary_section = False
        for index in range(length + 1):
            if index < length:
                history_values = history_values_lst[index]
            else:
                is_summary_section = True
                history_values = {
                    'internal_ref': _('Total'),
                    'barcode': '',
                    'name': '',
                    'quantity': '',
                    'standard_price': '',
                    'value': 'SUM({}:{})',
                }
            for col_pos, column in enumerate(self.columns):
                cell_type = self.info_labels.get(column).get('type', '')
                cell_format = self.info_labels.get(column).get(
                    'format', self.format_default)
                cell_value = history_values.get(column, '')

                if is_summary_section:
                    cell_format = self.format_table_header

                if cell_type == 'formula':
                    cell_value = cell_value or '{}*{}'
                    start_cell = xl_rowcol_to_cell(row_pos, col_pos - 2)
                    stop_cell = xl_rowcol_to_cell(row_pos, col_pos - 1)

                    if is_summary_section:
                        cell_format = self.format_table_number_bold
                        start_cell = xl_rowcol_to_cell(start_row_pos, col_pos)
                        stop_cell = xl_rowcol_to_cell(stop_row_pos, col_pos)

                    cell_formula_value = cell_value.format(
                        start_cell, stop_cell)
                    self.sheet.write_formula(
                        row_pos, col_pos, cell_formula_value, cell_format)
                else:
                    self.sheet.write(
                        row_pos, col_pos, cell_value, cell_format)

            stop_row_pos = row_pos
            row_pos += 1
        self.row_pos = row_pos

    def _define_formats(self, workbook):
        # ---------------------------------------------------------------------
        # Common
        # ---------------------------------------------------------------------
        format_config = {
            'font_size': 10,
            'valign': 'vcenter',
            'text_wrap': True,
        }
        self.format_default = workbook.add_format(format_config)

        format_bold = format_config.copy()
        format_bold.update({
            'bold': True,
        })
        self.format_bold = workbook.add_format(format_bold)
        # ---------------------------------------------------------------------
        # Report Title
        # ---------------------------------------------------------------------
        format_report_title = format_config.copy()
        format_report_title.update({
            'bold': True,
            'align': 'center',
            'font_size': 36,
        })
        self.format_report_title = workbook.add_format(format_report_title)

        # ---------------------------------------------------------------------
        # Table format
        # ---------------------------------------------------------------------
        format_table = format_config.copy()
        format_table.update({
            'font_size': 11,
            'bold': True,
            'align': 'vcenter',
        })
        self.format_table = workbook.add_format(format_table)
        self.format_table.set_bg_color('#0070c0')
        self.format_table.set_font_color('#ffffff')

        format_table_header = format_table.copy()
        format_table_header.update({
            'font_size': 10,
        })
        self.format_table_header = workbook.add_format(format_table_header)
        self.format_table_header.set_bg_color('#d9d9d9')
        self.format_table_header.set_font_color('#000000')

        format_table_number = format_table.copy()
        format_table_number.update({
            'font_size': 10,
            'bold': False,
        })
        self.format_table_number = workbook.add_format(
            format_table_number)
        self.format_table_number.set_num_format('#,##0.0000')

        format_table_number_bold = format_table.copy()
        format_table_number_bold.update({
            'font_size': 10,
        })
        self.format_table_number_bold = workbook.add_format(
            format_table_number_bold)
        self.format_table_number_bold.set_num_format('#,##0.0000')
        self.format_table_number_bold.set_bg_color('#d9d9d9')
        self.format_table_number_bold.set_font_color('#000000')


ReportStockInventoryXlsx(
    'report.stock_inventory_xlsx',
    'wizard.valuation.history',
)
