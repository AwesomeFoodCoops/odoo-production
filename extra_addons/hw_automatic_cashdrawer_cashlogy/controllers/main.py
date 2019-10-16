# -*- encoding: utf-8 -*-
##############################################################################
#
#    Hardware Telium Payment Terminal module for Odoo
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    Copyright (C) 2019 Druidoo (https://www.druidoo.io)
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

import simplejson
import socket
import time
import json
import traceback
from threading import Thread, Lock
from Queue import Queue, Empty

import openerp.addons.hw_proxy.controllers.main as hw_proxy
from openerp import http


import logging
_logger = logging.getLogger(__name__)

BUFFER_SIZE = 1024
KEEPALIVE_TIME_LIMIT = 120
KEEPALIVE_INTERVAL = 30
SOCKET_TIMEOUT = 30


class CashlogyAutomaticCashdrawerDriver(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.lock = Lock()
        self.queue = Queue()
        self.device_name = "Automatic Cashdrawer"
        self.socket = False
        self.status = {'status': 'disconnected', 'messages': ['Stand by..']}
        self.config = {}
        self._keepalive_tick = time.time()  # Last keepalive check

    def lockedstart(self):
        with self.lock:
            if not self.isAlive():
                self.daemon = True
                self.start()

    def push_task(self, task, data=None):
        self.lockedstart()
        self.queue.put((time.time(), task, data))

    def _check_keep_alive(self):
        if (time.time() - self._keepalive_tick) >= KEEPALIVE_INTERVAL:
            self._keepalive_tick = time.time()
            if (
                self.status.get('status') == 'connected' and
                (time.time() - self._keepalive_tick) >= KEEPALIVE_TIME_LIMIT
            ):
                _logger.debug('Disconnected because of timeout')
                self.disconnect()

    def run(self):
        while True:
            try:
                self._check_keep_alive()
                # Non blocking queue
                try:
                    timestamp, task, data = self.queue.get(False)
                except Empty:
                    continue
                # Process tasks
                if task == 'connect':
                    self.connect(data)
            except Exception as e:
                self.set_status('error', repr(e))
                errmsg = str(e) + '\n'
                errmsg += '-' * 60 + '\n'
                errmsg += traceback.format_exc()
                errmsg += '-' * 60 + '\n'
                _logger.error(errmsg)
            except (KeyboardInterrupt, SystemExit):
                # TODO: Not working as expected..
                _logger.debug('Shutdown signaled. Shutting down connection..')
                self.disconnect()

    def value_float(self, value):
        '''
        Utility function to transform a string '2000'
        into a float 20.00
        '''
        if isinstance(value, basestring):
            return float(value) / 100
        elif isinstance(value, int):
            return float(value)
        elif isinstance(value, float):
            return value
        else:
            raise TypeError('Unrecognized type for value_float: %s' % value)

    def get_status(self):
        return self.status

    def set_status(self, status, message=None):
        if not self.status:
            self.status = {}
        if status == self.status.get('status'):
            if (
                message and
                message not in self.status.setdefault('messages', [])
            ):
                self.status['messages'].append(message)
                if status == 'error' and message:
                    _logger.error('Cashlogy Error: %s' % message)
                elif status == 'disconnected' and message:
                    _logger.warning('Disconnected Cashlogy: %s' % message)
        else:
            self.status['status'] = status
            self.status['messages'] = [message] if message else []
            if status == 'error' and message:
                _logger.error('Cashlogy Error: %s' % message)
            elif status == 'disconnected' and message:
                _logger.info('Disconnected Cashlogy: %s', message)

    def connect(self, config):
        '''
        Connects to CashlogyConnector
        Returns True if success
        '''
        if not config:
            config = {}
        host = config.get('host')
        port = int(config.get('port', 0))
        if not host or not port:
            self.set_status(
                'error',
                'Configuration error (host: %s, port: %s)' % (host, port))
            return False
        # Connect and initialize
        try:
            _logger.debug('Cashlogy is connecting')
            self.set_status('connecting')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(SOCKET_TIMEOUT)
            self.socket.connect((host, port))
            # Initialize Cashlogy
            _logger.debug('Cashlogy initializing..')
            self.set_status('connecting', 'Initializing..')
            # Do we need to initialize
            res = self.send(['I'])
            if len(res) != 2:
                raise Exception('Invalid initialize response: %s' % res)
            if res[0] != '0':
                raise Exception('Initialization error: %s' % res)
            self.set_status('connected')
            self.config = config
            # Start thread
            self.lockedstart()
            return True
        except Exception as e:
            self.set_status('error', repr(e))
            return False

    def disconnect(self):
        '''
        Sends the disconnect command and closes the connection
        '''
        if self.status.get('status') == 'connected':
            res = self.send(['E'])
        self.set_status(
            'disconnected',
            'No request to connect from POS. Standing by..')

    def keepalive(self, config=None, force=False):
        '''
        Connects to CashlogyConnector and initializes it, if needed.
        If not called in KEEPALIVE_TIME_LIMIT, the connection will be
        closed by the keepalive timer.

        @TODO: KEEPALIVE timer is not implemented yet.

        If force=True, it will force reconnect even if there's an error

        Returns get_status()
        '''
        status = self.status.get('status')
        if (
            config and status == 'disconnected' or
            force and status not in ['connected', 'connecting']
        ):
            self.lockedstart()
            self.push_task('connect', config)
        return self.get_status()

    def _send(self, msg):
        '''
            Raw implementation to send a message and get a response
        '''
        with self.lock:
            try:
                self.socket.send(msg)
                return self.socket.recv(BUFFER_SIZE)
            except Exception as e:
                self.set_status('error', repr(e))
                raise e

    def send(self, msg, raw=False):
        '''
        Sends message to the CashlogyConnector and waits for a response
        It will try to auto connect, if connection configuration has been
        previously provided

        Params
            msg    accepts either '#I#0#1#' or ['I', 0, 1]
        Returns a response parsed as list, where # is the delimiter
        '''
        if isinstance(msg, basestring):
            pass
        else:
            iter(msg)  # It will raise a TypeError exception if not iterable
            # Smart-transform arguments into string
            for i, v in enumerate(msg):
                if isinstance(v, basestring):
                    continue
                elif isinstance(v, bool):
                    msg[i] = str(int(v))
                elif isinstance(v, int):
                    msg[i] = str(v)
                elif isinstance(v, float):
                    msg[i] = str(int(v * 100))
                else:
                    _logger.debug('Unrecognized param: %s' % v)
                    msg[i] = str(v)
            msg = '#%s#' % '#'.join(msg)
        res_raw = self._send(msg)
        res = res_raw.strip('#').split('#')
        if len(res) >= 1:
            if res[0].startswith('ER:'):
                raise Exception(
                    'Cashlogy error: %s (%s)' % (res_raw, msg))
            elif res[0].startswith('WR:'):
                _logger.warning(
                    'Cashlogy warning: %s (%s)' % (res_raw, msg))
        if raw:
            return res_raw
        return res

    def display_backoffice(self):
        '''
        This function display the backoffice on the cashier screen.
        '''
        return self.send("#G#1#1#1#1#1#1#1#1#1#1#1#1#1#")

    def get_inventory(self):
        '''
        Gets the content of the cashdrawer

        Returns {total: {}, recycler: {}, stacker: {}) where each item is a
        dict with the following format: {denomination: count}
        '''
        res = self.send(['Y'])
        # Parse response
        recycler = {
            self.value_float(i[0]): int(i[1])
            for i in [
                p.split(':') for p in res[1].replace(';', ',').split(',')
            ]}
        stacker = {
            self.value_float(i[0]): int(i[1])
            for i in [
                p.split(':') for p in res[2].replace(';', ',').split(',')
            ]}
        # Compute totals
        totals = {
            v: recycler.get(v, 0) + stacker.get(v, 0)
            for v in set(recycler.keys() + stacker.keys())
        }
        # Return response
        return {
            'recycler': recycler,
            'stacker': stacker,
            'total': totals,
        }

    def get_total_amount(self):
        '''
        Gets the total amount of the cashdrawer inventory

        Returns {total: 0.00, recycler: 0.00, stacker: 0.00}
        '''
        res = self.send(['T'])
        recycler = self.value_float(res[1])
        stacker = self.value_float(res[2])
        return {
            'recycler': recycler,
            'stacker': stacker,
            'total': recycler + stacker,
        }

    def dispense(self, amount, options=None):
        '''
        Dispenses the selected amount

        Returns ['WR:LEVEL', amount, 0] if success
        '''
        if not options:
            options = {}
        amount = float(amount)
        res = self.send([
            'P', amount, False, options.get('only_coins', False)])
        return self.value_float(res[1])

    def start_add_change(self):
        '''
        Sets the machine to add money.
        It will remain in this state until stop_acceptance()
        '''
        return self.send(['A', 2])

    def start_acceptance(self):
        '''
        Sets the machine to load cash.
        I don't know the difference with add_change, but I think
        this one is intented for sale operations.
        '''
        return self.send(['B', 0])

    def get_amount_accepted(self):
        '''
        Returns the amount accepted by the machine so far
        '''
        res = self.send(['Q'])
        return self.value_float(res[1])

    def stop_acceptance(self):
        '''
        Stops the loading operation
        Returns the amount loaded
        '''
        res = self.send(['J'])
        return self.value_float(res[1])

    def display_transaction_start(self, amount, options):
        '''
        Sets the machine to receive money from the customer.
        Result is {amount: 0.00}
        '''
        # Send message and wait for confirmation
        amount = float(amount)
        operation_number = options.get('operation_number', '00000')
        msg = ['C', operation_number, 1, amount, 15, 15, 1, 1, 1, 0, 0]
        res = self.send(msg)
        # Check response
        amount_in = self.value_float(res[1])
        amount_out = self.value_float(res[2])
        amount = amount_in - amount_out
        return amount

    def display_close_till(self):
        '''
        Displays the backoffice till closure wizard.
        Returns dict with:
        - total_before: 0.00    Total amount of money the machine had before
        - added:        0.00    Total amount added
        - total:        0.00    Total amount that remains on the machine
        - dispensed:    0.00    Total dispensed
        '''
        res = self.send(['F', True], blocking=True)
        res = {
            'total_before': self.value_float(res[1]),
            'added': self.value_float(res[2]),
            'total': self.value_float(res[3]),
        }
        res['dispensed'] = res['total_before'] + res['added'] - res['total']
        return res

    def display_complete_emptying(self):
        '''
        Displays the backoffice complete emptying wizard.
        Returns the amount delivered
        '''
        res = self.send(['V', True, ''], blocking=True)
        return self.value_float(res[1])

    def display_empty_stacker(self):
        '''
        Displays the backoffice empty stacker wizard.
        Returns the amount that has been removed from the stacker
        '''
        res = self.send(['S', True], blocking=True)
        return self.value_float(res[1])


driver = CashlogyAutomaticCashdrawerDriver()
hw_proxy.drivers['automatic_cashdrawer'] = driver


class CashlogyAutomaticCashdrawerProxy(hw_proxy.Proxy):

    @http.route()
    def status_json(self):
        '''
        Overload status_json to keep the Cashdrawer connection alive
        This method is called frecuently by the POS, if there's a session
        '''
        driver.keepalive()
        return super(CashlogyAutomaticCashdrawerProxy, self).status_json()

    @http.route(
        '/hw_proxy/cashlogy/connect', type='json', auth='none', cors='*')
    def cashlogy_connect(self, config):
        '''
        Receives the connection configuration, and attempts to reconnect
        if necessary.
        '''
        return driver.keepalive(config, True)

    @http.route(
        '/hw_proxy/cashlogy/<string:cmd>', type='json', auth='none', cors='*')
    def cashlogy_command(self, cmd, **kwargs):
        if cmd not in [
            'initialize',
            'start_add_change', 'start_acceptance',
            'get_amount_accepted', 'stop_acceptance',
            'dispense', 'get_inventory', 'get_total_amount',
            'display_transaction_start',
            'display_close_till',
            'display_complete_emptying',
            'display_empty_stacker',
            'display_backoffice',
        ]:
            raise Exception('Invalid command: %s' % cmd)
        return getattr(driver, cmd)(**kwargs)
