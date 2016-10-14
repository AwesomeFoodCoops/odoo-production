# -*- encoding: utf-8 -*-
##############################################################################
#
#    Hardware Telium Payment Terminal module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import logging
import simplejson
from threading import Thread, Lock
import openerp.addons.hw_proxy.controllers.main as hw_proxy
from openerp import http
import socket


logger = logging.getLogger(__name__)


class CashlogyAutomaticCashdrawerDriver(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lock = Lock()
        self.cashdrawer_status = {'status': 'connecting', 'messages': []}
        self.device_name = "Cashlogy automatic cashdrawer"
        self.socket = False

    def get_status(self):
        return self.cashdrawer_status

    def set_status(self, cashdrawer_status, message=None):
        if cashdrawer_status == self.cashdrawer_status['status']:
            if message is not None and message != self.cashdrawer_status['messages'][-1]:
                self.cashdrawer_status['messages'].append(message)
        else:
            self.cashdrawer_status['cashdrawer_status'] = cashdrawer_status
            if message:
                self.cashdrawer_status['messages'] = [message]
            else:
                self.cashdrawer_status['messages'] = []

        if cashdrawer_status == 'error' and message:
            logger.error('Cashlogy Error: ' + message)
        elif cashdrawer_status == 'disconnected' and message:
            logger.warning('Cashlogy Disconnected: ' + message)

    def send_to_cashdrawer(self, msg):
        if (self.socket is not False):
            try:
                BUFFER_SIZE = 1024
#                 answer = "ok"
                self.socket.send(msg)
                answer = self.socket.recv(BUFFER_SIZE)
                if msg == '#I#':
                    self.set_status('initialized')
                return answer
            except Exception, e:
                logger.error('Impossible to send to cashdrawer: %s' % str(e))
                if self.socket is False:
                    self.set_status('disconnected')

    def cashlogy_connection_check(self, connection_info):
        '''This function initialize the cashdrawer.
        '''
        if self.socket is False:
            connection_info_dict = simplejson.loads(connection_info)
            assert isinstance(connection_info_dict, dict), \
                'connection_info_dict should be a dict'
            ip_address = connection_info_dict.get('ip_address')
            tcp_port = connection_info_dict.get('tcp_port')
            if tcp_port:
                tcp_port = int(tcp_port)
            # TODO: handle this case, maybe pop up or display
            # on the screen like WiFi button
            if not ip_address or not tcp_port:
                logger.warning('Configuration error, please configure '
                               'ip_address and tcp_port.')
                self.set_status('disconnected')
            else:
                try:
                    self.socket = socket.socket(socket.AF_INET,
                                                socket.SOCK_STREAM)
                    self.socket.connect((ip_address, tcp_port))
                    self.set_status('connected')
                except Exception, e:
                    logger.error('Impossible to connect the cashdrawer: %s' % str(e))
                    self.set_status('disconnected')

    def cashlogy_connection_init(self, connection_info):
        '''This function initialize the cashdrawer.
        '''
        self.socket = False
        if self.socket is False:
            self.cashlogy_connection_check(connection_info)
        answer = self.send_to_cashdrawer("#I#")
        return answer

    def cashlogy_connection_exit(self):
        '''This function close the connection with the cashdrawer.
        '''
        answer = self.send_to_cashdrawer("#E#")
        return answer

    def display_backoffice(self):
        '''This function display the backoffice on the cashier screen.
        '''
        # All this "1" are active button to be display on the screen
        message = "#G#1#1#1#1#1#1#1#1#1#1#1#1#1#"
        answer = self.send_to_cashdrawer(message)
        return answer

    def transaction_start(self, payment_info):
        '''This function sends the data to the serial/usb port.
        '''
        payment_info_dict = simplejson.loads(payment_info)
        assert isinstance(payment_info_dict, dict), \
            'payment_info_dict should be a dict'
        amount = int(payment_info_dict['amount'] * 100)  # amount is sent in cents to the cashdrawer
        operation_number = payment_info_dict.get('operation_number', '00001')  # Number to be able to track operation
        display_accept_button = payment_info_dict.get('display_accept_button', False)  # Allow the user to confirm the change given by customer
        screen_on_top = payment_info_dict.get('screen_on_top', False)  # Put the screen on top
        see_customer_screen = payment_info_dict.get('see_customer_screen', False)  # Display customer screen
        message = "#C#%s#1#%s#%s#15#15#%s#1#%s#0#0#" % (operation_number,
                                                        amount,
                                                        int(see_customer_screen),
                                                        int(display_accept_button),
                                                        int(screen_on_top))
        answer = self.send_to_cashdrawer(message)
        # Cancel (18€ given, 18€ given back)
        # answer = "#WR:CANCEL#1800#1800#0#0#"
        # Validated (20€ given, 2€ given back)
        # answer = "#WR:LEVEL#1700#0#0#0#"
        return answer


driver = CashlogyAutomaticCashdrawerDriver()

hw_proxy.drivers['cashlogy_automatic_cashdrawer'] = driver


class CashlogyAutomaticCashdrawerProxy(hw_proxy.Proxy):

    @http.route(
        '/hw_proxy/automatic_cashdrawer_connection_check',
        type='json', auth='none', cors='*')
    def automatic_cashdrawer_connection_check(self, connection_info):
        logger.info(
            'Cashlogy: Call automatic_cashdrawer_connexion_check with '
            'connection_info=%s', connection_info)
        answer = driver.cashlogy_connection_check(connection_info)
        return {'info': str(answer)}

    @http.route(
        '/hw_proxy/automatic_cashdrawer_connection_init',
        type='json', auth='none', cors='*')
    def automatic_cashdrawer_connection_init(self, connection_info):
        logger.info(
            'Cashlogy: Call automatic_cashdrawer_connexion_init with '
            'connection_info=%s', connection_info)
        answer = driver.cashlogy_connection_init(connection_info)
        return {'info': str(answer)}

    @http.route(
        '/hw_proxy/automatic_cashdrawer_connection_exit',
        type='json', auth='none', cors='*')
    def automatic_cashdrawer_connection_exit(self, info=None):
        logger.debug(
            'Cashlogy: Call automatic_cashdrawer_connexion_exit')
        answer = driver.cashlogy_connection_exit()
        return {'info': str(answer)}

    @http.route(
        '/hw_proxy/automatic_cashdrawer_transaction_start',
        type='json', auth='none', cors='*')
    def automatic_cashdrawer_transaction_start(self, payment_info=None):
        logger.debug(
            'Cashlogy: Call automatic_cashdrawer_transaction_start with '
            'payment_info=%s', payment_info)
        answer = driver.transaction_start(payment_info)
        return {'info': str(answer)}

    @http.route(
        '/hw_proxy/automatic_cashdrawer_display_backoffice',
        type='json', auth='none', cors='*')
    def automatic_cashdrawer_display_backoffice(self, backoffice_info=None):
        logger.debug(
            'Cashlogy: Call display_backoffice without info')
        answer = driver.display_backoffice()
        return {'info': str(answer)}
