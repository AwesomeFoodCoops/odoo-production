# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: Druidoo (<http://www.druidoo.io/>)
# @author: Druidoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import time
import fnmatch
import zipfile
import logging
import os
from dateutil import parser
import datetime

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
    parent_supplier_id = fields.Many2one(comodel_name="res.partner", string="EDI Parent supplier",
                                         domain=[('supplier', '=', True), ('is_edi', '=', True)])
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
    price_mapping_ids = fields.One2many(comodel_name="edi.price.mapping", inverse_name="price_config_id")
    ble_mapping_ids = fields.One2many(comodel_name="edi.ble.mapping", inverse_name="ble_config_id")
    delivery_sign = fields.Char(string="Delivery sign")
    days = fields.Integer(string="Frequency check (days)")
    header_code = fields.Char(string="Header code")
    lines_code = fields.Char(string="Lines code")
    fnmatch_filter = fields.Char(string="Fnmatch Filter", default="CH*")

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
            ftp.connect(edi_system.ftp_host, int(edi_system.ftp_port))
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
                f_name = datetime.datetime.now().strftime(pattern)
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
        except Exception, e:
            raise ValidationError(_("Error when pushing order file:\n %s") % tools.ustr(e))

    @api.model
    def ftp_connection_pull_prices(self, ftp, distant_folder_path, local_folder_path, fnmatch_filter='CH*'):
        try:
            today = datetime.date.today()
            ftp.cwd(distant_folder_path)
            names = ftp.nlst()
            for name in names:
                if fnmatch.fnmatch(name, fnmatch_filter):
                    timestamp = ftp.voidcmd("MDTM " + distant_folder_path + "/" + name)[4:].strip()
                    file_date = parser.parse(timestamp)
                    diff = today - file_date.date()
                    days_gap = diff.days
                    if days_gap < 7:
                        with open(os.path.join(local_folder_path, name), "wb") as f:
                            ftp.retrbinary("RETR {}".format(name), f.write)
                        zf = zipfile.ZipFile(os.path.join(local_folder_path, name))
                        zf.extractall(local_folder_path)
                        zf.close()
                        name_without_zip = name[:-4]
                        file = open(os.path.join(local_folder_path, name_without_zip), "r")
                        return file.readlines(), name
        except Exception, e:
            raise ValidationError(_("Error when pulling prices update file:\n %s") % tools.ustr(e))\

    @api.model
    def ftp_connection_pull_ble(self, ftp, edi_system, distant_folder_path, local_folder_path):
        try:
            today = datetime.date.today()
            ftp.cwd(distant_folder_path)
            names = ftp.nlst()
            for name in names:
                if fnmatch.fnmatch(name, "BLE*"):
                    timestamp = ftp.voidcmd("MDTM " + distant_folder_path + "/" + name)[4:].strip()
                    file_date = parser.parse(timestamp)
                    diff = today - file_date.date()
                    days_gap = diff.days
                    if days_gap < edi_system.days:
                        with open(os.path.join(local_folder_path, name), "wb") as f:
                            ftp.retrbinary("RETR {}".format(name), f.write)
                        zf = zipfile.ZipFile(os.path.join(local_folder_path, name))
                        zf.extractall(local_folder_path)
                        zf.close()
                        name_without_zip = name[:-4]
                        file = open(os.path.join(local_folder_path, name_without_zip), "r")
                        return file.readlines(), name
        except Exception, e:
            raise ValidationError(_("Error when pulling BLE update file:\n %s") % tools.ustr(e))

    @api.model
    def get_datenow_format_for_file(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        date = now.split(' ')[0].replace('-', '')
        hour = now.split(' ')[1].replace(':', '')
        return date, hour

    @api.model
    def get_datetime_format_ddmmyyyy(self, date):
        do_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return "%02d%02d%s" % (do_date.day, do_date.month, str(do_date.year)[2:])

    @api.model
    def get_date_format_yyyymmdd(self, date):
        """
        Transform a string date to datetime and format it to standard odoo date format
        """
        return datetime.datetime.strptime(date, "%y%m%d").strftime('%Y-%m-%d')\

    @api.model
    def get_date_format_ble_yyyymmdd(self, date):
        """
        Transform a string date (specific to delivery order interface format) to datetime object and format it to standard odoo date format
        """
        return datetime.datetime.strptime(date, "%Y%m%d").strftime('%Y-%m-%d')


    @api.model
    def insert_separator(self, string, index, separator):
        """
            This method is to insert a separator inside string on a certain position
        """
        return string[:index] + separator + string[index:]

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
