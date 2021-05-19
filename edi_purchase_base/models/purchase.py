# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.net/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from odoo import models, api, fields, _, tools
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    date_planned = fields.Datetime(
        string="Scheduled Date",
        compute="_compute_date_planned",
        index=True,
        store=True,
        copy=True,
    )

    @api.multi
    def _consolidate_products(self):
        """
            Consolidate order lines by product.
            Raise if Tax or price different.
            @return: dict {product_id(record):[code_or_ean, qty, price,\
            taxes(records)]}
        """
        self.ensure_one()
        if not self.order_line:
            raise ValidationError(_("No lines in this order %s!") % self.name)
        lines = {}
        for line in self.order_line:
            if line.product_id in lines:
                if line.taxes_id != lines[line.product_id]["taxes_id"]:
                    raise ValidationError(
                        _("Check taxes for lines with product %s!")
                        % line.product_id.name
                    )
                if line.price_unit != lines[line.product_id]["price_unit"]:
                    raise ValidationError(
                        _("Check price for lines with product %s!")
                        % line.product_id.name
                    )
                lines[line.product_id]["quantity"] += line.product_qty
            else:
                code, origin_code = line.product_id._get_supplier_code_or_ean(
                    line.partner_id
                )
                values = {
                    "code": code,
                    "origin_code": origin_code,
                    "quantity": line.product_qty,
                    "price_unit": line.price_unit,
                    "taxes_id": line.taxes_id,
                }
                lines.update({line.product_id: values})
        return lines

    @api.multi
    def _get_data_from_mapping_config(self, order_lines, edi):
        """
            Data From mapping
        """
        self.ensure_one()
        data = """"""
        try:
            for line in edi.mapping_ids:
                data += safe_eval(line.value, {
                    'self': self,
                    'order_lines': order_lines,
                    'edi': edi
                    })
        except Exception as e:
            raise ValidationError(
                _("Error in python code mapping values:\n %s") % tools.ustr(e)
            )
        return data

    @api.multi
    def _prepare_data_lines(self, lines, edi):
        """
            Data lines to send
        """
        self.ensure_one()
        data = """%sA%sB%s%s%s""" % (
            edi.constant_file_start,
            edi.vrp_code,
            edi.customer_code,
            self._get_data_from_mapping_config(lines, edi),
            edi.constant_file_end,
        )
        return data

    @api.multi
    def _process_send_ftp(self):
        """
            Process Send FTP
        """
        self.ensure_one()
        ecs_obj = self.env["edi.config.system"]
        config_obj = self.env["ir.config_parameter"]
        # Consolidated lines
        lines = self._consolidate_products()
        # Check EDI System config
        edi_system = ecs_obj.search(
            [("supplier_id", "=", self.partner_id.id)], limit=1
        )
        if not edi_system:
            raise ValidationError(
                _("No Config FTP for this supplier %s!") % self.partner_id.name
            )
        # Prepare data file
        data_lines = self._prepare_data_lines(lines, edi_system)
        # Params
        pattern = safe_eval(edi_system.po_text_file_pattern, {'self': self})
        distant_folder_path = edi_system.csv_relative_in_path
        local_folder_path = config_obj.sudo().get_param("edi.local_folder_path")
        # Open FTP
        ftp = ecs_obj.ftp_connection_open(edi_system)
        # Send
        ecs_obj.ftp_connection_push_order_file(
            ftp,
            distant_folder_path,
            local_folder_path,
            pattern,
            data_lines,
            encoding="utf-8",
        )
        # Log
        self.env["purchase.edi.log"].create_log_history(
            _("Orders interface"), edi_system.id
        )
        # Close FTP
        ecs_obj.ftp_connection_close(ftp)
        return True

    @api.multi
    def button_confirm(self):
        """
        Override: Send FTP.
        """
        res = super(PurchaseOrder, self).button_confirm()
        for order in self.filtered(lambda l: l.partner_id.is_edi):
            order._process_send_ftp()
        return res
