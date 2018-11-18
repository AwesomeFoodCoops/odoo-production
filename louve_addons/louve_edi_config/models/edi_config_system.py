# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import time
import logging
import os
from datetime import datetime

from openerp import models, api, fields

_logger = logging.getLogger(__name__)

try:
    from ftplib import FTP
except ImportError:
    _logger.warning(
        "Cannot import 'ftplib' Python Librairy. 'louve_edi_config'"
        " module will not work properly.")


class EdiConfigSystem(models.Model):
    _name = 'edi.config.system'

    name = fields.Char(string="Name", required=True)
    supplier_id = fields.Many2one(comodel_name="res.partner", string="EDI supplier",
                                  domain=[('supplier', '=', True), ('is_edi', '=', True)], required=True)
    ftp_host = fields.Char(string="FTP Server Host", default='xxx.xxx.xxx.xxx', required=True)
    ftp_port = fields.Char(string="FTP Server Port", default='21', required=True)
    ftp_login = fields.Char(string="FTP Login", required=True)
    ftp_password = fields.Char(string="FTP Password", required=True)
    csv_relative_in_path = fields.Char(string="Relative path for IN interfaces", default='/', required=True)
    csv_relative_out_path = fields.Char(string="Relative path for OUT interfaces", default='/', required=True)
    po_text_file_pattern = fields.Char(string="Purchase order File pattern",
                                       default="'LD%sH%s.C99' % self.env['edi.config.system'].get_datenow_file_format()",
                                       required=True)
    do_text_file_pattern = fields.Char(string="Delivery order File pattern")
    pricing_text_file_pattern = fields.Char(string="Pricing File pattern")
    customer_code = fields.Char(string="Customer code", default='33513', required=True)
    constant_file_start = fields.Char(string="Constant file start", default='HDIAPAR', required=True)
    constant_file_end = fields.Char(string="Constant file end", default='*DIAPAR*DIAPAR', required=True)
    vrp_code = fields.Char(string="VRP Code", default='03', required=True)
    mapping_ids = fields.One2many(comodel_name="edi.mapping.lines", inverse_name="config_id")

    @api.model
    def ftp_connection_open(self, edi_system):
        """Return a new FTP connection with found parameters."""
        _logger.info("Trying to connect to ftp://%s@%s:%d" % (
            edi_system.ftp_login, edi_system.ftp_host,
            edi_system.ftp_port))
        try:
            ftp = FTP()
            ftp.connect(edi_system.ftp_host, edi_system.ftp_port)
            if edi_system.ftp_login:
                ftp.login(
                    edi_system.ftp_login,
                    edi_system.ftp_password)
            else:
                ftp.login()
            return ftp
        except:
            _logger.error("Connection to ftp://%s@%s:%d failed." % (
                edi_system.ftp_login, edi_system.ftp_host,
                edi_system.ftp_port))
            return False

    @api.model
    def ftp_connection_close(self, ftp):
        try:
            ftp.quit()
        except:
            pass

    @api.model
    def ftp_connection_push_order_file(self, ftp, distant_folder_path, local_folder_path,
                                       pattern, lines, encoding='utf-8'):
        if lines:
            # Generate temporary file
            f_name = datetime.now().strftime(pattern)
            local_path = os.path.join(local_folder_path, f_name)
            distant_path = os.path.join(distant_folder_path, f_name)
            f = open(local_path, 'w')
            for line in lines:
                raw_text = line
                f.write(raw_text.encode(encoding, errors='ignore'))
            f.close()

            # Send File by FTP
            f = open(local_path, 'r')
            ftp.storbinary('STOR ' + distant_path, f)
            f.close()
            # Delete temporary file
            os.remove(local_path)

    @api.model
    def get_datenow_format_for_file(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        date = now.split(' ')[0].replace('-', '')
        hour = now.split(' ')[1].replace(':', '')
        return date, hour
