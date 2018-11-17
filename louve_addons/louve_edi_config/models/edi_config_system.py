# -*- coding: utf-8 -*-
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html

import ftplib
import base64

from openerp import models, api, _, tools
from openerp.exceptions import ValidationError


class FtpConfig(models.AbstractModel):
    _name = 'ftp.config'

    def get_ftp_param(self):
        return {
            'host': self.env['ir.config_parameter'].get_param('ftp_host'),
            'user': self.env['ir.config_parameter'].get_param('ftp_user'),
            'password': self.env['ir.config_parameter'].get_param('ftp_password'),
            'directory': self.env['ir.config_parameter'].get_param('ftp_directory')
        }

    @api.model
    def ftp_transfert(self, file_path=False, file_name=False):
        try:
            if not file_path or not file_name:
                raise ValidationError(_('There is no file path / file name'))
            ftp_params = self.get_ftp_param()
            session = ftplib.FTP(ftp_params['host'], ftp_params['user'], ftp_params['password'])
            session.cwd(ftp_params['directory'])
            ftp_file = open(file_path, 'rb')
            session.storbinary('STOR %s' % file_name, ftp_file)
            ftp_file.close()
            session.quit()
        except Exception, e:
            raise ValidationError(tools.ustr(e))
