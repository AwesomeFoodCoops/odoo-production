# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import datetime
from odoo import models, api, tools, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    def _get_supplier_code_or_ean(self, seller_id):
        """
        """
        self.ensure_one()
        code, origin_code = "", ""
        seller_line = self.seller_ids.filtered(
            lambda l: l.name == seller_id and l.product_code
        )
        if seller_line and seller_line[0].product_code:
            code = seller_line[0].product_code
            origin_code = "supplier"
        elif self.barcode:
            code = self.barcode
            origin_code = "barcode"
        if not code:
            raise ValidationError(
                _("No code for this product %s!") % self.name
            )
        return code, origin_code

    @api.model
    def remove_file(self, ftp, name, edi_system):
        try:
            path_to_file = edi_system.csv_relative_out_path
            ftp.delete("/".join([path_to_file, name]))
        except Exception as e:
            raise ValidationError(
                _("Error when removing file from ftp server : %s")
                % tools.ustr(e)
            )

    @api.model
    def read_prices_file(self, lines, edi_system):
        """
        This method is reponsible of reading supplier prices file, and
        integrate data into Odoo database according to fields mappping on the
        supplier ftp system configuration
        :param lines: Prices file lines (Python list)
               edi_system: EDI configuration system used
        :return: Boolean
        """
        edi_config = self.env["edi.config.system"]
        price_list_obj = self.env["supplier.price.list"]
        product_supp_info = self.env["product.supplierinfo"]
        if not lines:
            raise ValidationError(_(
                "Please configure fields mapping for prices interface on your \
                EDI system!"
            ))
        _logger.info(
            ">>>>>>>>>>>>>>>> Reading supplier prices file >>>>>>>>>>>>>>>>>>>"
        )
        prices = []
        value = []
        today = datetime.date.today()
        for line in lines:
            # check if this line is already imported.
            product_code_mapp = edi_system.price_mapping_ids.filtered(
                lambda rec: rec.mapping_field_id.name == "supplier_code"
            )
            pos_from = product_code_mapp.sequence_start
            pos_to = product_code_mapp.sequence_end
            product_code = line[pos_from:pos_to]
            if product_code in value:
                continue
            key = ["supplier_id", "import_date"]
            value = [edi_system.supplier_id.id, today]
            for mapping in edi_system.price_mapping_ids:
                slice_from = mapping.sequence_start
                slice_to = mapping.sequence_end
                # construct dictionary
                key.append(mapping.mapping_field_id.name)
                data = line[slice_from:slice_to]
                # Product test
                if mapping.mapping_field_id.name == "supplier_code":
                    # appending supplier_code data
                    value.append(data)
                    # appending product_id data
                    supp_info = product_supp_info.search(
                        [("product_code", "=", data)], limit=1
                    )
                    product_id = supp_info.product_tmpl_id.id
                    key.append("product_tmpl_id")
                    value.append(product_id)
                # Date test
                elif mapping.is_date:
                    # slice dates
                    apply_date = edi_config.get_date_format_yyyymmdd(data)
                    value.append(apply_date)
                # numeric test
                elif mapping.is_numeric:
                    decimal_precision = mapping.decimal_precision
                    price = edi_config.insert_separator(
                        data, -decimal_precision, "."
                    )
                    value.append(price)
                elif mapping.mapping_field_id.name == "product_name":
                    value.append(data)
            prices_dict = {k: v for k, v in zip(key, value)}
            prices.append(prices_dict)
        _logger.info(
            ">>>>>>>>>>>>>>> Creating supplier prices >>>>>>>>>>>>>>>>>>>>>>>>"
        )
        price_list_obj.bulk_create(prices)
        return True

    @api.model
    def cron_update_purchase_prices(self):
        ecs_obj = self.env["edi.config.system"]
        config_obj = self.env["ir.config_parameter"]
        partner_obj = self.env["res.partner"]
        partner_ids = partner_obj.search([("is_edi", "=", True)])
        # Check EDI System config
        edi_systems = ecs_obj.search([("supplier_id", "in", partner_ids.ids)])
        if not edi_systems:
            raise ValidationError(_(
                "No Configuration found for EDI suppliers on the whole system!"
            ))
        # Prices interface is only for parent suppliers, any segmentation is \
        # not considered by the EDI system FTP
        # operations.
        edi_systems_list = [
            edi_system
            for edi_system in edi_systems
            if not edi_system.parent_supplier_id
        ]
        # Prepare parameters
        for edi_system in edi_systems_list:
            distant_folder_path = edi_system.csv_relative_out_path
            local_folder_path = config_obj.sudo().get_param("edi.local_folder_path")
            # Open FTP
            ftp = ecs_obj.ftp_connection_open(edi_system)
            # Pull
            line_prices, file_name = ecs_obj.ftp_connection_pull_prices(
                ftp, distant_folder_path, local_folder_path,
                edi_system.fnmatch_filter
            )
            if not line_prices:
                continue
            # File Treatment and delete file
            if self.read_prices_file(line_prices, edi_system):
                self.remove_file(ftp, file_name, edi_system)
            # Log
            self.env["purchase.edi.log"].create_log_history(
                _("Prices interface"), edi_system.id
            )
            # Close FTP
            ecs_obj.ftp_connection_close(ftp)
        return True


class ProductSupplierinfo(models.Model):
    _inherit = "product.supplierinfo"

    @api.model
    def compute_edi_partner(self, partner_id):
        """
        :param partner_id: purchase order/invoice supplier
        :return: EDI supplier used in FTP prices operations
        """
        ecs_obj = self.env["edi.config.system"]
        edi_system = ecs_obj.search(
            [("supplier_id", "=", partner_id.id)], limit=1
        )
        if not edi_system:
            raise ValidationError(
                _("No Config FTP for this supplier %s!") % partner_id.name
            )
        if edi_system.parent_supplier_id:
            return edi_system.parent_supplier_id
        else:
            return edi_system.supplier_id

    @api.model
    def update_purchase_price(self, vals):
        """
            Looks for most recent price on purchase table of prices, only for
            EDI suppliers
            :param vals:
            :return: updated values with product price
        """
        supplier_id = vals.get("name", False)
        supplier = self.env["res.partner"].browse(supplier_id)
        if supplier.is_edi:
            edi_supplier = self.compute_edi_partner(supplier)
            supplier_code = vals.get("product_code", False)
            if not supplier_code:
                raise ValidationError(
                    _("Please give a supplier code to create the product!")
                )
            price = self.env["supplier.price.list"].search([
                ("supplier_id", "=", edi_supplier.id),
                ("supplier_code", "=", supplier_code),
            ], order="import_date DESC")
            if price:
                vals.update({"base_price": price[0].price})
        return vals

    @api.model
    def create(self, vals):
        vals = self.update_purchase_price(vals)
        return super(ProductSupplierinfo, self).create(vals)
