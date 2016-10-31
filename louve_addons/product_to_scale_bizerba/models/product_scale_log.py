# -*- coding: utf-8 -*-
# Copyright (C) 2014 GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import logging
from datetime import datetime

from openerp import tools
from openerp.osv import fields
from openerp.osv.orm import Model

_logger = logging.getLogger(__name__)

try:
    from ftplib import FTP
except ImportError:
    _logger.warning(
       "Cannot import 'ftplib' Python Librairy. 'product_to_scale_bizerba'"
       " module will not work properly.")


class product_scale_log(Model):
    _name = 'product.scale.log'
    _inherit = 'ir.needaction_mixin'
    _order = 'log_date desc, id desc'

    _EXTERNAL_SIZE_ID_RIGHT = 4

    _DELIMITER = '#'

    _ACTION_SELECTION = [
        ('create', 'Creation'),
        ('write', 'Update'),
        ('unlink', 'Deletion'),
    ]

    _ACTION_MAPPING = {
        'create': 'C',
        'write': 'C',
        'unlink': 'S',
    }

    _ENCODING_MAPPING = {
        'iso-8859-1': '\r\n',
    }

    _EXTERNAL_TEXT_ACTION_CODE = 'C'

    _EXTERNAL_TEXT_DELIMITER = '#'

    # Private Section
    def _clean_value(self, value, product_line):
        if not value:
            return ''
        elif product_line.multiline_length:
            res = ''
            current_val = value
            while current_val:
                res += current_val[:product_line.multiline_length]
                current_val = current_val[product_line.multiline_length:]
                if current_val:
                    res += product_line.multiline_separator
        else:
            res = value
        if product_line.delimiter:
            return res.replace(product_line.delimiter, '')
        else:
            return res

    def _generate_external_text(self, value, product_line, external_id, log):
        external_text_list = [
            self._EXTERNAL_TEXT_ACTION_CODE,                    # WALO Code
            log.product_id.scale_group_id.external_identity,    # ABNR Code
            external_id,                                        # TXNR Code
            self._clean_value(value, product_line),             # TEXT Code
        ]
        return self._EXTERNAL_TEXT_DELIMITER.join(external_text_list)

    # Compute Section
    def _compute_text(
            self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for log in self.browse(cr, uid, ids, context):

            group = log.product_id.scale_group_id
            product_text =\
                self._ACTION_MAPPING[log.action] + self._DELIMITER
            external_texts = []

            # Set custom fields
            for product_line in group.scale_system_id.product_line_ids:
                if product_line.field_id:
                    value = getattr(log.product_id, product_line.field_id.name)

                if product_line.type == 'id':
                    product_text += str(log.product_id.id)

                elif product_line.type == 'numeric':
                    value = tools.float_round(
                        value * product_line.numeric_coefficient,
                        precision_rounding=product_line.numeric_round)
                    product_text += str(value).replace('.0', '')

                elif product_line.type == 'text':
                    product_text += self._clean_value(value, product_line)

                elif product_line.type == 'external_text':
                    external_id = str(log.product_id.id)\
                        + str(product_line.id).rjust(
                            self._EXTERNAL_SIZE_ID_RIGHT, '0')
                    external_texts.append(self._generate_external_text(
                        value, product_line, external_id, log))
                    product_text += external_id

                elif product_line.type == 'constant':
                    product_text += self._clean_value(
                        product_line.constant_value, product_line)

                elif product_line.type == 'external_constant':
                    # Constant Value are like product ID = 0
                    external_id = str(product_line.id)

                    external_texts.append(self._generate_external_text(
                        product_line.constant_value, product_line, external_id,
                        log))
                    product_text += external_id

                elif product_line.type == 'many2one':
                    # If the many2one is defined
                    if value and not product_line.related_field_id:
                        product_text += value.id
                    elif value and product_line.related_field_id:
                        item_value = getattr(
                            value, product_line.related_field_id.name)
                        product_text +=\
                            item_value and str(item_value) or ''

                elif product_line.type == 'many2many':
                    # Select one value, depending of x2many_range
                    if product_line.x2many_range < len(value):
                        item = value[product_line.x2many_range - 1]
                        if product_line.related_field_id:
                            item_value = getattr(
                                item, product_line.related_field_id.name)
                        else:
                            item_value = item.id
                        product_text += self._clean_value(
                            item_value, product_line)

                elif product_line.type == 'product_image':
                    product_text += str(log.product_id.id) +\
                        product_line.suffix

                if product_line.delimiter:
                    product_text += product_line.delimiter
            break_line = self._ENCODING_MAPPING[log.scale_system_id.encoding]
            res[log.id] = {
                'product_text': product_text + break_line,
                'external_text': break_line.join(external_texts) + break_line,
                'external_text_display': '\n'.join(
                    [x.replace('\n', '') for x in external_texts]),
            }
        return res

    # Column Section
    _columns = {
        'log_date': fields.datetime('Log Date', required=True),
        'scale_system_id': fields.many2one(
            'product.scale.system', string='Scale System', required=True),
        'product_id': fields.many2one(
            'product.product', string='Product'),
        'product_text': fields.function(
            _compute_text, type='text', string='Product Text',
            multi='compute_text', store={'product.scale.log': (
                lambda self, cr, uid, ids, context=None:
                    ids, ['scale_system_id', 'product_id'], 10)}),
        'external_text': fields.function(
            _compute_text, type='text', string='External Text',
            multi='compute_text', store={'product.scale.log': (
                lambda self, cr, uid, ids, context=None: ids, [
                    'scale_system_id', 'product_id', 'product_id'], 10)}),
        'external_text_display': fields.function(
            _compute_text, type='text', string='External Text (Display)',
            multi='compute_text', store={'product.scale.log': (
                lambda self, cr, uid, ids, context=None: ids, [
                    'scale_system_id', 'product_id', 'product_id'], 10)}),
        'action': fields.selection(
            _ACTION_SELECTION, string='Action', required=True),
        'sent': fields.boolean(string='Is Sent'),
        'last_send_date': fields.datetime('Last Send Date'),
    }

    # View Section
    def _needaction_count(self, cr, uid, domain=None, context=None):
        return len(
            self.search(cr, uid, [('sent', '=', False)], context=context))

    def ftp_connection_open(self, cr, uid, scale_system, context=None):
        """Return a new FTP connection with found parameters."""
        _logger.info("Trying to connect to ftp://%s@%s" % (
            scale_system.ftp_login, scale_system.ftp_url))
        try:
            ftp = FTP(scale_system.ftp_url)
            if scale_system.ftp_login:
                ftp.login(
                    scale_system.ftp_login,
                    scale_system.ftp_password)
            else:
                ftp.login()
            return ftp
        except:
            _logger.error("Connection to ftp://%s@%s failed." % (
                scale_system.ftp_login, scale_system.ftp_url))
            return False

    def ftp_connection_close(self, cr, uid, ftp, context=None):
        try:
            ftp.quit()
        except:
            pass

    def ftp_connection_push_text_file(
            self, cr, uid, ftp, distant_folder_path, local_folder_path,
            pattern, lines, encoding, context=None):
        if lines:
            # Generate temporary file
            f_name = datetime.now().strftime(pattern)
            local_path = os.path.join(local_folder_path, f_name)
            distant_path = os.path.join(distant_folder_path, f_name)
            f = open(local_path, 'w')
            for line in lines:
                f.write(line.encode(encoding))
            f.close()

            # Send File by FTP
            f = open(local_path, 'r')
            ftp.storbinary('STOR ' + distant_path, f)

            # Delete temporary file
            os.remove(local_path)

    def send_log(self, cr, uid, ids, context=None):
        config_obj = self.pool['ir.config_parameter']
        folder_path = config_obj.get_param(
            cr, uid, 'bizerba.local_folder_path', context=context)

        system_map = {}
        for log in self.browse(cr, uid, ids, context=context):
            if log.scale_system_id in system_map.keys():
                system_map[log.scale_system_id].append(log)
            else:
                system_map[log.scale_system_id] = [log]

        for scale_system, logs in system_map.iteritems():

            # Open FTP Connection
            ftp = self.ftp_connection_open(
                cr, uid, logs[0].scale_system_id, context=context)
            if not ftp:
                return False

            # Generate and Send Files
            now = datetime.now()
            product_text_lst = []
            external_text_lst = []

            for log in logs:
                if log.product_text:
                    product_text_lst.append(log.product_text)
                if log.external_text:
                    external_text_lst.append(log.external_text)
            self.ftp_connection_push_text_file(
                cr, uid, ftp, scale_system.csv_relative_path,
                folder_path, scale_system.external_text_file_pattern,
                external_text_lst, scale_system.encoding, context=context)
            self.ftp_connection_push_text_file(
                cr, uid, ftp, scale_system.csv_relative_path,
                folder_path, scale_system.product_text_file_pattern,
                product_text_lst, scale_system.encoding, context=context)

            # Close FTP Connection
            self.ftp_connection_close(cr, uid, ftp, context=context)

            # Mark logs as sent
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.write(
                cr, uid, [log.id for log in logs], {
                    'sent': True,
                    'last_send_date': now,
                }, context=context)
        return True

    def cron_send_to_scale(self, cr, uid, context=None):
        log_ids = self.search(
            cr, uid, [('sent', '=', False)], order='log_date', context=context)
        self.send_log(cr, uid, log_ids, context=context)
