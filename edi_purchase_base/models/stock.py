# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, api, tools, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)


class StockPicking(models.Model):
    _inherit = "stock.picking"

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
    def read_stock_picking_file(self, lines, edi_system):
        """
        This method is reponsible of reading supplier DO file, and integrate \
        data into Odoo database according to fields mappping on the supplier \
        ftp system configuration
        :param lines: BLE(Electronic Delivery order) file lines (Python list)
               edi_system: EDI configuration system used
        :return: Boolean
        """
        edi_config = self.env["edi.config.system"]
        product_supp_info = self.env["product.supplierinfo"]
        picking_updated = self.env["picking.update"]
        if not lines:
            raise ValidationError(_(
                "Please configure fields mapping for BLE interface on your \
                EDI system!"
            ))
        _logger.info(
            ">>>>>>>>>>>>>>>>>> Reading BLE file >>>>>>>>>>>>>>>>>>>>>"
        )
        delivery_date = ""
        delivery_sign = ""
        picking_order = self.env["stock.picking"]
        supp_info = self.env["product.supplierinfo"]
        proposition_vals = dict()
        values_list = []
        for line in lines:
            # This condition ensures that this job consider only one picking \
            # per EDI File
            if line[0] == edi_system.header_code and not delivery_date:
                # Header processing
                delivery_date_mapp = edi_system.ble_mapping_ids.filtered(
                    lambda rec: rec.mapping_field_id.name == "date_planned"
                )
                pos_from = delivery_date_mapp.sequence_start
                pos_to = delivery_date_mapp.sequence_end
                data = line[pos_from:pos_to]
                delivery_date = edi_config.get_date_format_ble_yyyymmdd(data)
            elif line[0] == edi_system.lines_code:
                # Look if it's a first delivery
                delivery_sign = edi_system.delivery_sign
                if delivery_sign == "-":
                    break
                # Look for picking_order
                code_mapping = edi_system.ble_mapping_ids.filtered(
                    lambda rec: rec.mapping_field_id.name == "product_code"
                )
                pos_from = code_mapping.sequence_start
                pos_to = code_mapping.sequence_end
                product_code = line[pos_from:pos_to]
                if not picking_order:
                    supp_info = product_supp_info.search(
                        [("product_code", "=", product_code)], limit=1
                    )
                    supplier_ids = supp_info.mapped("name")
                    # Look for corresponding purchase order, normally it \
                    # should be just one even if there is more than one
                    # supplier associated to product
                    if supplier_ids:
                        cr = self.env.cr
                        cr.execute(
                            "select * from purchase_order where "
                            "cast (date_planned as date) = %s and partner_id \
                            in %s limit 1",
                            (delivery_date, tuple(supplier_ids.ids)),
                        )
                        res_po = cr.fetchone()
                        res_id = res_po and res_po[0] or False
                        po = self.env["purchase.order"].browse(res_id)
                        # Assuming purchase order has only one picking order \
                        # associated.
                        if po:
                            picking_order = po.picking_ids[0]
                # Look for updated quantity
                qty_mapping = edi_system.ble_mapping_ids.filtered(
                    lambda rec: rec.mapping_field_id.name == "product_qty"
                )
                pos_from = qty_mapping.sequence_start
                pos_to = qty_mapping.sequence_end
                product_qty_pack = line[pos_from:pos_to]
                # Look for ordered quantity
                product_tmpl_id = self.env["product.template"]
                if supp_info:
                    product_tmpl_id = supp_info[0].product_tmpl_id
                ordered_product_id = self.env["product.product"].search(
                    [("product_tmpl_id", "=", product_tmpl_id.id)], limit=1
                )
                cr = self.env.cr
                cr.execute(
                    "select * from stock_move_line where picking_id=%s \
                    and product_id=%s limit 1",
                    (picking_order.id, ordered_product_id.id),
                )
                res_stock = cr.fetchone()
                res_id = res_stock and res_stock[0] or False
                ordered_operation = self.env["stock.move.line"].browse(
                    res_id
                )
                ordered_quantity = ordered_operation.product_qty_package
                # Construct one2many values
                if ordered_quantity != float(product_qty_pack):
                    vals = dict()
                    vals.update(
                        {
                            "line_to_update_id": ordered_operation.id,
                            "product_id": ordered_product_id.id,
                            "ordered_quantity": ordered_quantity,
                            "product_qty": float(product_qty_pack),
                            "package_qty": ordered_operation.package_qty,
                        }
                    )
                    values_list += [(0, 0, vals)]
        if delivery_sign == "+":
            proposition_vals.update(
                {"name": picking_order.id, "values_proposed_ids": values_list}
            )
            _logger.info(
                ">>>>>>>>>>>>>>>> Creating delivery order update propositions \
                >>>>>>>>>>>>>>>>>>>"
            )
            picking_updated.create(proposition_vals)
            return True
        else:
            return True

    @api.model
    def cron_update_stock_picking(self):
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
            line_picking, file_name = ecs_obj.ftp_connection_pull_ble(
                ftp, edi_system, distant_folder_path, local_folder_path
            )
            if not line_picking:
                continue
            # File Treatment and delete file
            if self.read_stock_picking_file(line_picking, edi_system):
                self.remove_file(ftp, file_name, edi_system)
            # Log
            self.env["purchase.edi.log"].create_log_history(
                _("BLE interface"), edi_system.id
            )
            # Close FTP
            ecs_obj.ftp_connection_close(ftp)
        return True
