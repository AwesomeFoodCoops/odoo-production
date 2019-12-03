# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from xlsxwriter.utility import xl_rowcol_to_cell
from .image_util import get_record_image_path

from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx
from openerp.api import Environment
from openerp import SUPERUSER_ID
from openerp import fields


class ReportAccountAssetXlsx(ReportXlsx):

    def create_xlsx_report(self, ids, data, report):
        self.env = Environment(self.env.cr, SUPERUSER_ID, self.env.context)
        return super(ReportAccountAssetXlsx,
                     self).create_xlsx_report(ids, data, report)

    def generate_xlsx_report(self, workbook, data, objects):
        self.object = objects[0]
        self._define_formats(workbook)
        self.sheet = workbook.add_worksheet()
        self.setup_config()

        self.generate_report_title()
        self.generate_report_general()

        self.row_pos += 2
        self.table_columns = [
            'name',
            'state',
            'date',
            'value',
            'salvage_value',
            'method',
            'method_number',
            'prorata',
            'amo_ant',
            'amo_de_lan',
            'cum_amo',
            'value_residual'
        ]
        self.info_labels = {
            'name': {'str': u"Nom de l'immobilisation"},
            'state': {'str': 'Statut'},
            'date': {'str': 'Date', 'format': self.format_table_date},
            'value': {
                'str': 'Valeur brute',
                'type': 'formula',
                'format': self.format_table_number
            },
            'salvage_value': {
                'str': 'N/amortissable',
                'type': 'formula',
                'format': self.format_table_number
            },
            'method': {'str': u'Méthode'},
            'method_number': {'str': 'Nb. amort.'},
            'prorata': {'str': 'Prorata'},
            'amo_ant': {
                'str': 'Amo. ant.',
                'type': 'formula',
                'format': self.format_table_number
            },
            'amo_de_lan': {
                'str': u"Amortissement de l'année",
                'type': 'formula',
                'format': self.format_table_number
            },
            'cum_amo': {
                'str': 'Cum. amo.',
                'type': 'formula',
                'format': self.format_table_number
            },
            'value_residual': {
                'str': u'Val. résiduelle',
                'type': 'formula',
                'format': self.format_table_number
            },
        }
        category_datas_lst = data.get('category_datas_lst', [])
        self.summary_column_info = {
            'value': [],
            'value_residual': [],
            'salvage_value': [],
            'amo_ant': [],
            'amo_de_lan': [],
            'cum_amo': [],
            'val_nette': [],
        }
        for category_datas in category_datas_lst:
            self.generate_report_category(category_datas)
            self.row_pos += 1

        self.generate_report_summary()

    def setup_config(self):
        self.row_pos = 5
        self._set_default_format()

    def _set_default_format(self):
        self.sheet.set_default_row(20)
        self.sheet.set_column('A:Z', None, self.format_default)
        self.sheet.set_column('A:A', 40)
        self.sheet.set_column('B:L', 20)

    def generate_report_title(self):
        company = self.env.user.company_id
        company_logo = company.logo
        company_logo_path = get_record_image_path(
            record=company,
            image=company_logo,
        )
        if company_logo_path:
            self.sheet.insert_image(0, 0, company_logo_path)
        self.sheet.merge_range(
            'B2:K5',
            u'Immobilisations et amortissements',
            self.format_report_title)

    def generate_report_general(self):
        row_pos = self.row_pos
        col_pos = 0
        today = fields.Date.from_string(fields.Date.today())
        formated_today_str = today.strftime("%d/%m/%Y")
        created_by_header = u'Créé le : '
        created_uid = self.object._context.get('uid', self.env.uid)
        created_user = self.env['res.users'].browse(created_uid)
        created_by_info = '{} par {}'.format(
            formated_today_str, created_user.name)
        self.sheet.write_rich_string(
            row_pos, col_pos,
            self.format_bold, created_by_header,
            self.format_default, created_by_info
        )

        row_pos += 2
        from_date_header = u'Début : '
        from_date_dt = fields.Date.from_string(self.object.from_date)
        from_date_str = from_date_dt.strftime("%d/%m/%Y")
        self.sheet.write_rich_string(
            row_pos, col_pos,
            self.format_bold, from_date_header,
            self.format_default, from_date_str
        )
        row_pos += 1
        to_date_header = 'Fin : '
        to_date_dt = fields.Date.from_string(self.object.to_date)
        to_date_str = to_date_dt.strftime("%d/%m/%Y")
        self.sheet.write_rich_string(
            row_pos, col_pos,
            self.format_bold, to_date_header,
            self.format_default, to_date_str
        )

        self.row_pos = row_pos

    def generate_report_category(self, category_datas):
        row_pos = self.row_pos
        col_pos = 0

        category_name = category_datas.get('category_name', '')
        self.sheet.write(row_pos, col_pos, category_name, self.format_table)

        for i in range(1, 12):
            col_pos = i
            self.sheet.write(row_pos, col_pos, '', self.format_table)

        row_pos += 1
        column_labels = self.info_labels

        for col_index, column in enumerate(self.table_columns, 0):
            col_pos = col_index
            label_dict = column_labels.get(column)
            label_str = label_dict.get('str')
            cell_format = self.format_table_header
            self.sheet.write(row_pos, col_pos, label_str, cell_format)

        row_pos += 1
        category_data_lines = category_datas.get('lines', [])
        category_data_lines_length = len(category_data_lines)
        start_row_pos = row_pos

        for index in range(category_data_lines_length + 1):
            is_sub_summary_section = False
            if index < category_data_lines_length:
                line_data = category_data_lines[index]
            else:
                is_sub_summary_section = True
                stop_row_pos = row_pos - 1
                line_data = {
                    'name': 'Sous-total',
                    'value': '=SUM({}:{})',
                    'value_residual': '=SUM({}:{})',
                    'salvage_value': '=SUM({}:{})',
                    'amo_ant': '=SUM({}:{})',
                    'amo_de_lan': '=SUM({}:{})',
                    'cum_amo': '=SUM({}:{})',
                    'val_nette': '=SUM({}:{})',
                }
            for col_index, column in enumerate(self.table_columns, 0):
                col_pos = col_index
                cell_value = line_data.get(column, '')

                if isinstance(cell_value, bool):
                    cell_value = cell_value and 'Oui' or 'Non'

                cell_type = column_labels.get(column).get('type', '')
                cell_format = column_labels.get(column).get(
                    'format', self.format_default)
                need_to_write_summary_formula = \
                    is_sub_summary_section and cell_type == 'formula'

                if is_sub_summary_section:
                    cell_format = self.format_table_bold

                # Write formula
                if need_to_write_summary_formula:
                    cell_format = self.format_table_number_bold
                    start_cell = xl_rowcol_to_cell(start_row_pos, col_pos)
                    stop_cell = xl_rowcol_to_cell(stop_row_pos, col_pos)
                    cell_formula_value = \
                        cell_value.format(start_cell, stop_cell)
                    self.sheet.write_formula(
                        row_pos, col_pos, cell_formula_value, cell_format)

                    # append cell to summary section info
                    self.summary_column_info[column].append(
                        xl_rowcol_to_cell(row_pos, col_pos)
                    )
                else:
                    if column == 'date' and not is_sub_summary_section:
                        cell_format = self.format_table_date
                        cell_value = fields.Date.from_string(cell_value)

                    self.sheet.write(row_pos, col_pos, cell_value, cell_format)
            row_pos += 1

        self.row_pos = row_pos

    def generate_report_summary(self):
        row_pos = self.row_pos
        summary_data = {
            'name': u'Total général',
            'value': '=SUM({})',
            'value_residual': '=SUM({})',
            'salvage_value': '=SUM({})',
            'amo_ant': '=SUM({})',
            'amo_de_lan': '=SUM({})',
            'cum_amo': '=SUM({})',
            'val_nette': '=SUM({})',
        }
        cell_format = self.format_table_header_dark_grey
        for col_index, column in enumerate(self.table_columns, 0):
            col_pos = col_index
            cell_value = summary_data.get(column, '')
            if '=SUM' in cell_value:
                cell_format = self.format_table_number_bold_dark_grey
                cell_formula_value = cell_value.format(
                    ', '.join(self.summary_column_info[column])
                )
                self.sheet.write_formula(
                    row_pos, col_pos, cell_formula_value, cell_format)
            else:
                self.sheet.write(row_pos, col_pos, cell_value, cell_format)
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

        format_center = format_config.copy()
        format_center.update({
            'align': 'center',
        })
        self.format_center = workbook.add_format(format_center)

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

        format_title_table = format_config.copy()
        format_title_table.update({
            'bold': True,
            'align': 'center',
        })
        self.format_title_table = workbook.add_format(format_title_table)

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

        format_table_bold = format_table.copy()
        format_table_bold.update({
            'font_size': 10,
        })
        self.format_table_bold = workbook.add_format(format_table_bold)
        self.format_table_bold.set_bg_color('#d9d9d9')
        self.format_table_bold.set_font_color('#000000')

        format_table_bold_total = format_table.copy()
        format_table_bold_total.update({
            'font_size': 11,
            'align': 'right',
        })

        format_table_number = format_table.copy()
        format_table_number.update({
            'font_size': 10,
            'bold': False,
        })
        self.format_table_number = workbook.add_format(
            format_table_number)
        self.format_table_number.set_num_format('#,##0.00')

        format_table_number_bold = format_table.copy()
        format_table_number_bold.update({
            'font_size': 10,
        })
        self.format_table_number_bold = workbook.add_format(
            format_table_number_bold)
        self.format_table_number_bold.set_num_format('#,##0.00')
        self.format_table_number_bold.set_bg_color('#d9d9d9')
        self.format_table_number_bold.set_font_color('#000000')

        format_table_date = format_config.copy()
        format_table_date.update({
            'num_format': 'dd/mm/yyyy',
            'font_size': 10
        })
        self.format_table_date = workbook.add_format(format_table_date)

        self.format_table_header_dark_grey = workbook.add_format(
            format_table_header)
        self.format_table_header_dark_grey.set_bg_color('#808080')
        self.format_table_header_dark_grey.set_font_color('#000000')

        self.format_table_number_bold_dark_grey = workbook.add_format(
            format_table_number_bold)
        self.format_table_number_bold_dark_grey.set_num_format('#,##0.00')
        self.format_table_number_bold_dark_grey.set_bg_color('#808080')
        self.format_table_number_bold_dark_grey.set_font_color('#000000')


ReportAccountAssetXlsx(
    'report.report_account_asset_xlsx',
    'account.asset.xlsx.wizard',
)
