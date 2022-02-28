
from odoo import fields, models, _


class ReportGrossMarginXlsx(models.AbstractModel):
    _inherit = 'report.report_xlsx.abstract'
    _name = 'report.report_gross_margin_xlsx'
    _description = "Report Gross Margin XLSX"

    def generate_xlsx_report(self, workbook, data, objects):
        self.object = objects[0]
        self._define_formats(workbook)
        self.sheet = workbook.add_worksheet()
        self.setup_config()

        self.generate_report_title()
        self.generate_report_general()

        self.row_pos += 2
        self.table_columns = [
            "category",
            "pre_tax_net_sales",
            "inventory_value_beginning",
            "net_purchases",
            "total_available",
            "inventory_value_ending",
            "cogs",
            "gross_margin",
        ]
        self.info_labels = {
            "category": {"str": _("Category")},
            "pre_tax_net_sales": {
                "str": _("Pre-tax Net Sales during period"),
            },
            "inventory_value_beginning": {
                "str": _("Inventory Value at beginning date"),
                "format": self.format_table_number,
            },
            "net_purchases": {
                "str": _("Net purchases"),
                "format": self.format_table_number,
            },
            "total_available": {
                "str": _("Total available for Sale"),
                "format": self.format_table_number,
            },
            "inventory_value_ending": {
                "str": _("Inventory Value at end date"),
                "format": self.format_table_number,
            },
            "cogs": {
                "str": _("Cost of Goods Sold"),
                "format": self.format_table_number,
            },
            "gross_margin": {
                "str": _("Gross Margin"),
                "format": self.format_table_number,
            },
           
        }
        datas = objects and objects.get_datas() or []
        self.generate_report_content(datas)
        self.row_pos += 1

    def setup_config(self):
        self.row_pos = 1
        self._set_default_format()

    def _set_default_format(self):
        self.sheet.set_default_row(20)
        self.sheet.set_column("A:Z", None, self.format_default)
        self.sheet.set_column("A:A", 40)
        self.sheet.set_column("B:L", 20)

    def generate_report_title(self):
        self.sheet.merge_range(
            "A1:C1",
            _("GROSS MARGIN REPORT"),
            self.format_report_title,
        )

    def generate_report_general(self):
        row_pos = self.row_pos
        from_date_dt = fields.Datetime.context_timestamp(
            self, self.object.from_date)
        from_date_str = from_date_dt.strftime("%d/%m/%Y %H:%M:%S")
        to_date_dt = fields.Datetime.context_timestamp(
            self, self.object.to_date)
        to_date_str = to_date_dt.strftime("%d/%m/%Y %H:%M:%S")
        self.sheet.merge_range(
            "A2:C2",
            "{from_date} - {to_date}".format(
                from_date=from_date_str,
                to_date=to_date_str
            ),
            self.format_report_time_period,
        )
        self.row_pos = row_pos

    def generate_report_content(self, datas):
        row_pos = self.row_pos
        row_pos += 1
        categories = []
        pre_tax_net_sales = 0.0
        inventory_value_beginning = 0.0
        net_purchases = 0.0
        total_available = 0.0
        inventory_value_ending = 0.0
        cogs = 0.0
        gross_margin = 0.0

        for line_data in datas:
            categories.append(line_data['category'])
            pre_tax_net_sales += line_data.get("pre_tax_net_sales", 0)
            inventory_value_beginning += line_data.get("inventory_value_beginning", 0)
            net_purchases += line_data.get("net_purchases", 0)
            total_available += line_data.get("total_available", 0)
            inventory_value_ending += line_data.get("inventory_value_ending", 0)
            cogs += line_data.get("cogs", 0)
            gross_margin += line_data.get("gross_margin", 0)

        self.sheet.write(
            "A4",
            _("Sales"),
            self.format_bold,
        )
        self.sheet.write(
            "A6",
            _("Beginning inventory"),
            self.format_bold,
        )
        self.sheet.write(
            "A7",
            _("Purchases"),
            self.format_bold,
        )
        self.sheet.write(
            "A8",
            _("Goods available for sale"),
            self.format_bold,
        )
        self.sheet.write(
            "A9",
            _("End inventory"),
            self.format_bold,
        )
        self.sheet.write(
            "A10",
            _("Cost of goods sold"),
            self.format_bold,
        )
        self.sheet.write(
            "A12",
            _("Gross margin"),
            self.format_bold,
        )
        self.sheet.write(
            "A14",
            _("Product categories:"),
            self.format_default,
        )
        # VAlue
        self.sheet.write(
            "B4",
            pre_tax_net_sales,
            self.format_table_number,
        )
        self.sheet.write(
            "B6",
            inventory_value_beginning,
            self.format_table_number,
        )
        self.sheet.write(
            "B7",
            net_purchases,
            self.format_table_number,
        )
        self.sheet.write(
            "B8",
            total_available,
            self.format_table_number,
        )
        self.sheet.write(
            "B9",
            inventory_value_ending,
            self.format_table_number,
        )
        self.sheet.write(
            "B10",
            cogs,
            self.format_table_number,
        )
        self.sheet.write(
            "B12",
            gross_margin,
            self.format_table_number,
        )
        self.sheet.write_formula(
            "C4",
            "=B4/B4",
            self.format_table_number_percen,
        )
        self.sheet.write_formula(
            "C10",
            "=B10/B4",
            self.format_table_number_percen,
        )
        self.sheet.write_formula(
            "C12",
            "=B12/B4",
            self.format_table_number_percen,
        )
        self.row_pos = 15
        for categ in categories:
            self.sheet.write(
                "A{row}".format(row=self.row_pos),
                categ,
                self.format_default,
            )
            self.row_pos += 1

    def _define_formats(self, workbook):
        # ---------------------------------------------------------------------
        # Common
        # ---------------------------------------------------------------------
        format_config = {
            "font_size": 11,
            "valign": "vcenter",
            "text_wrap": True,
        }
        self.format_default = workbook.add_format(format_config)

        format_bold = format_config.copy()
        format_bold.update(
            {"bold": True}
        )
        self.format_bold = workbook.add_format(format_bold)

        format_center = format_config.copy()
        format_center.update(
            {"align": "center"}
        )
        self.format_center = workbook.add_format(format_center)

        # ---------------------------------------------------------------------
        # Report Title
        # ---------------------------------------------------------------------
        format_report_title = format_config.copy()
        format_report_title.update(
            {"bold": True, "bg_color": "#5b9bd5"}
        )
        self.format_report_title = workbook.add_format(format_report_title)
        format_report_time_period = format_config.copy()
        format_report_time_period.update(
            {"bold": True, "bg_color": "#00b0f0"}
        )
        self.format_report_time_period = workbook.add_format(format_report_time_period)

        format_title_table = format_config.copy()
        format_title_table.update(
            {"bold": True, "align": "center"}
        )
        self.format_title_table = workbook.add_format(format_title_table)

        # ---------------------------------------------------------------------
        # Table format
        # ---------------------------------------------------------------------
        format_table = format_config.copy()
        format_table.update(
            {"font_size": 11, "bold": True, "align": "vcenter"}
        )
        self.format_table = workbook.add_format(format_table)
        self.format_table.set_bg_color("#0070c0")
        self.format_table.set_font_color("#ffffff")

        format_table_header = format_table.copy()
        format_table_header.update(
            {"font_size": 11}
        )
        self.format_table_header = workbook.add_format(format_table_header)
        self.format_table_header.set_bg_color("#d9d9d9")
        self.format_table_header.set_font_color("#000000")

        format_table_bold = format_table.copy()
        format_table_bold.update(
            {"font_size": 11}
        )
        self.format_table_bold = workbook.add_format(format_table_bold)
        self.format_table_bold.set_bg_color("#d9d9d9")
        self.format_table_bold.set_font_color("#000000")

        format_table_bold_total = format_table.copy()
        format_table_bold_total.update(
            {"font_size": 11, "align": "right"}
        )

        format_table_number = format_table.copy()
        format_table_number.update(
            {"font_size": 11, "bold": False}
        )
        self.format_table_number = workbook.add_format(format_table_number)
        self.format_table_number.set_num_format("#,##0.00 {sb}".format(
            sb=self.env.user.company_id.currency_id.symbol))

        format_table_number_percen = format_table.copy()
        format_table_number_percen.update(
            {"font_size": 11, "bold": False}
        )
        self.format_table_number_percen = workbook.add_format(format_table_number_percen)
        self.format_table_number_percen.set_num_format("#,##0.00%")
        

        format_table_number_bold = format_table.copy()
        format_table_number_bold.update(
            {"font_size": 11}
        )
        self.format_table_number_bold = workbook.add_format(
            format_table_number_bold
        )
        self.format_table_number_bold.set_num_format("#,##0.00")
        self.format_table_number_bold.set_bg_color("#d9d9d9")
        self.format_table_number_bold.set_font_color("#000000")

        format_table_date = format_config.copy()
        format_table_date.update({"num_format": "dd/mm/yyyy", "font_size": 11})
        self.format_table_date = workbook.add_format(format_table_date)

        self.format_table_header_dark_grey = workbook.add_format(
            format_table_header
        )
        self.format_table_header_dark_grey.set_bg_color("#808080")
        self.format_table_header_dark_grey.set_font_color("#000000")

        self.format_table_number_bold_dark_grey = workbook.add_format(
            format_table_number_bold
        )
        self.format_table_number_bold_dark_grey.set_num_format("#,##0.00")
        self.format_table_number_bold_dark_grey.set_bg_color("#808080")
        self.format_table_number_bold_dark_grey.set_font_color("#000000")
