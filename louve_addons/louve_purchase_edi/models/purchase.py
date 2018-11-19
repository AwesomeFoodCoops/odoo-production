# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

from datetime import datetime # Used when eval python codes !!

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def _consolidate_products(self):
        """
            Consolidate order lines by product.
            Raise if Tax or price different.
            @return: dict {product_id(record):[ qty, price, taxes(records)]}
        """
        self.ensure_one()
        if not self.order_line:
            raise ValidationError(_("No lines in this order %s!") % self.name)
        lines = {}
        for line in self.order_line:
            if line.product_id in lines:
                if line.taxes_id != lines[line.product_id][2]:
                    raise ValidationError(_("Check taxes for lines with product %s!") % line.product_id.name)
                if line.price_unit != lines[line.product_id][1]:
                    raise ValidationError(_("Check price for lines with product %s!") % line.product_id.name)
                lines[line.product_id][0] += line.product_qty
            else:
                lines.update({line.product_id: [line.product_qty, line.price_unit, line.taxes_id]})
        return lines

    @api.multi
    def _get_data_from_mapping_config(self, lines, edi):
        """
            Data From mapping
        """
        self.ensure_one()
        data = """"""
        for line in edi.mapping_ids:
            data += eval(line.value)
            # RAF traitement des order_line et le nombre de caractere
        return data

    @api.multi
    def _prepare_data_lines(self, lines, edi):
        """
            Data lines to send
        """
        self.ensure_one()
        data = """%s\nA%sB%s%s%s""" % (edi.constant_file_start,
                                       edi.vrp_code,
                                       edi.customer_code,
                                       self._get_data_from_mapping_config(lines, edi),
                                       edi.constant_file_end)
        return data

    @api.multi
    def _process_send_ftp(self):
        """
            Process Send FTP
        """
        self.ensure_one()
        ecs_obj = self.env['edi.config.system']
        config_obj = self.env['ir.config_parameter']
        # Consolidated lines
        lines = self._consolidate_products()
        # Check EDI System config
        edi_system = ecs_obj.search([('supplier_id', '=', self.partner_id.id)], limit=1)
        if not edi_system:
            raise ValidationError(_("No Config FTP for this supplier %s!") % self.partner_id.name)
        # Prepare data file
        data_lines = self._prepare_data_lines(lines, edi_system)
        # Params
        pattern = eval(edi_system.po_text_file_pattern)
        distant_folder_path = edi_system.csv_relative_in_path
        local_folder_path = config_obj.get_param('edi.local_folder_path')
        # Open FTP
        ftp = ecs_obj.ftp_connection_open(edi_system)
        # Send
        ecs_obj.ftp_connection_push_order_file(ftp,
                                               distant_folder_path,
                                               local_folder_path,
                                               pattern,
                                               data_lines,
                                               encoding='utf-8')
        # Log
        
        # Close FTP
        ecs_obj.ftp_connection_close(ftp)
        return True


    @api.multi
    def button_confirm(self):
        """
        Override: 1.Consolidated lines.
                  2.Send FTP.
        """
        for order in self:
            # Send FTP
            order._process_send_ftp()
        return super(PurchaseOrder, self).button_confirm()
