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
import telium
import time
from threading import Thread, Lock
from Queue import Queue
import openerp.addons.hw_proxy.controllers.main as hw_proxy
from openerp import http

logger = logging.getLogger(__name__)


class TeliumPaymentTerminalDriver(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.queue = Queue()
        self.lock = Lock()
        self.status = {'status': 'connecting', 'messages': []}

    def get_status(self):
        self.push_task('status')
        return self.status

    def set_status(self, status, message=None):
        if status == self.status['status']:
            if message is not None and message != self.status['messages'][-1]:
                self.status['messages'].append(message)
        else:
            self.status['status'] = status
            if message:
                self.status['messages'] = [message]
            else:
                self.status['messages'] = []

        if status == 'error' and message:
            logger.error('Payment Terminal Error: '+message)
        elif status == 'disconnected' and message:
            logger.warning('Disconnected Terminal: '+message)

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def push_task(self, task, data=None):
        self.lockedstart()
        self.queue.put((time.time(), task, data))


    def transaction_start(self,payment_info):
        #logger = Logger_p()
        '''This function sends the data to the serial/usb port.
        '''
        payment_info_dict = simplejson.loads(payment_info)
        assert isinstance(payment_info_dict, dict), \
            'payment_info_dict should be a dict'
        answer = {}
        try:
            my_device = telium.Telium('/dev/ttyACM0')
            amount = float(payment_info_dict['amount'])
            if payment_info_dict['payment_mode'] == 'check':
                payment_mode = telium.TERMINAL_TYPE_PAYMENT_CHECK
            elif payment_info_dict['payment_mode'] == 'card':
                payment_mode = telium.TERMINAL_TYPE_PAYMENT_CARD
            else:
                logger.error(
                "The payment mode '%s' is not supported"
                % payment_info_dict['payment_mode'])
                return False

            my_payment = telium.TeliumAsk(
                '1',  # Checkout ID 1
                telium.TERMINAL_ANSWER_SET_FULLSIZED,  # Ask for fullsized repport
                telium.TERMINAL_MODE_PAYMENT_DEBIT,  # Ask for debit
                payment_mode,  # Using a card or a check
                telium.TERMINAL_NUMERIC_CURRENCY_EUR,
                telium.TERMINAL_REQUEST_ANSWER_WAIT_FOR_TRANSACTION,  # Wait for transaction to end before getting final answer
                telium.TERMINAL_FORCE_AUTHORIZATION_DISABLE,  # Let device choose if we should ask for authorization
                amount  # Ask for 12.5 EUR
            )
            try:
                if not my_device.ask(my_payment):
                    logger.error('Unable to init payment on device.')
                    return False
            except telium.TerminalInitializationFailedException as e:
                logger.error(format(e))
                return False

            # Wait for terminal to answer
            my_answer = my_device.verify(my_payment)

            if my_answer is not None:
                # Print answered data from terminal
                logger.debug(my_answer.__dict__)
                answer = {
                    'pos_number': my_answer.__dict__['_pos_number'],
                    'transaction_result': my_answer.__dict__['_transaction_result'],
                    'amount_msg': float(my_answer.__dict__['_amount'])*100, #TODO : delete *100 here and simulatnously /100 in https://github.com/AwesomeFoodCoops/odoo-production/blob/9.0/extra_addons/po$
                    'payment_mode': my_answer.__dict__['_payment_mode'],
                    'payment_terminal_return_message': my_answer.__dict__,
                }
                logger.debug('answer = %s' % answer)
        except Exception as e:
            logger.error('Error : %s' % str(e))
        return answer

    def run(self):
        while True:
            try:
                timestamp, task, data = self.queue.get(True)
                if task == 'transaction_start':
                    self.transaction_start(data)
                elif task == 'status':
                    pass
            except Exception as e:
                self.set_status('error', str(e))

driver = TeliumPaymentTerminalDriver()

hw_proxy.drivers['telium_payment_terminal'] = driver


class TeliumPaymentTerminalProxy(hw_proxy.Proxy):
    @http.route(
        '/hw_proxy/payment_terminal_transaction_start',
        type='json', auth='none', cors='*')
    def payment_terminal_transaction_start(self, payment_info):
        logger.debug(
            'Telium: Call payment_terminal_transaction_start with '
            'payment_info=%s', payment_info)
        driver.push_task('transaction_start', payment_info)

    @http.route(
        '/hw_proxy/payment_terminal_transaction_start_with_return',
        type='json', auth='none', cors='*')
    def payment_terminal_transaction_start_with_return(self, payment_info):
        logger.debug(
            'Telium: Call payment_terminal_transaction_start with return '
            'payment_info=%s', payment_info)
        answer = driver.transaction_start(payment_info)
        logger.debug(answer)
        return answer
