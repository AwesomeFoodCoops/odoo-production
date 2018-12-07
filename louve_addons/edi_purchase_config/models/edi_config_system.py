# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import time
import logging
import os
from datetime import datetime

from openerp import models, api, fields, tools, _
from openerp.exceptions import ValidationError

_logger = logging.getLogger(__name__)

try:
    from ftplib import FTP
except ImportError:
    _logger.warning(
        "Cannot import 'ftplib' Python Librairy. 'edi_purchase_config'"
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
    po_text_file_pattern = fields.Char(string="Purchase order File pattern", required=True)
    do_text_file_pattern = fields.Char(string="Delivery order File pattern")
    pricing_text_file_pattern = fields.Char(string="Pricing File pattern")
    customer_code = fields.Char(string="Customer code", required=True)
    constant_file_start = fields.Char(string="Constant file start", required=True)
    constant_file_end = fields.Char(string="Constant file end", required=True)
    vrp_code = fields.Char(string="VRP Code", required=True)
    mapping_ids = fields.One2many(comodel_name="edi.mapping.lines", inverse_name="config_id")

    @api.one
    @api.constrains('ftp_port')
    def _check_ftp_port(self):
        if not self.ftp_port.isdigit():
            raise ValidationError(_("FTP port must be numeric!"))

    @api.model
    def ftp_connection_open(self, edi_system):
        """Return a new FTP connection with found parameters."""
        _logger.info("Trying to connect to ftp://%s@%s:%s" % (
            edi_system.ftp_login, edi_system.ftp_host,
            edi_system.ftp_port))
        try:
            ftp = FTP()
            ftp.connect(edi_system.ftp_host)
            if edi_system.ftp_login:
                ftp.login(
                    edi_system.ftp_login,
                    edi_system.ftp_password)
            else:
                ftp.login()
            return ftp
        except Exception, e:
            raise ValidationError(_("Error when opening FTP connection:\n %s") % tools.ustr(e))

    @api.model
    def ftp_connection_close(self, ftp):
        try:
            ftp.quit()
        except Exception, e:
            raise ValidationError(_("Error when closing FTP connection:\n %s") % tools.ustr(e))

    @api.model
    def ftp_connection_push_order_file(self, ftp, distant_folder_path, local_folder_path,
                                       pattern, lines, encoding='utf-8'):
        try:
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
                print("Chemin distant : %s" % distant_path)
                ftp.storbinary('STOR ' + distant_path, f)
                f.close()
                # Delete temporary file
                os.remove(local_path)
        except Exception, e:
            raise ValidationError(_("Error when pushing order file:\n %s") % tools.ustr(e))

    @api.model
    def get_datenow_format_for_file(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        date = now.split(' ')[0].replace('-', '')
        hour = now.split(' ')[1].replace(':', '')
        return date, hour

    @api.model
    def get_datetime_format_ddmmyyyy(self, date):
        do_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return "%02d%02d%s" % (do_date.day, do_date.month, str(do_date.year)[2:])

    @api.model
    def _fix_lenght(self, value, lenght, mode='float', replace='', position='before'):
        """
            Mode = string/integer
            replace ==> ' ' or '0'
            position ==> before / after
        """
        value = str(value)
        if mode == 'float':
            value = value.split('.')[0]
        if position == 'before':
            value = ''.join([replace for i in range(lenght - len(value))]) + value
        else:
            value += ''.join([replace for i in range(lenght - len(value))])
        return value[0:lenght]
