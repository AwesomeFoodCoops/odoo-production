/*
    POS Payment Terminal module for Odoo
    Copyright (C) 2014-2016 Aurélien DUMAINE
    Copyright (C) 2014-2015 Akretion (www.akretion.com)
    @author: Aurélien DUMAINE
    @author: Alexis de Lattre <alexis.delattre@akretion.com>
    The licence is in the file __openerp__.py
*/

odoo.define('pos_payment_terminal.pos_payment_terminal', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');
    var devices = require('point_of_sale.devices');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    models.load_fields("account.journal", ['payment_mode']);

    models.Paymentline = models.Paymentline.extend({
        get_automatic_payment_terminal: function() {
            if (this.cashregister.journal.payment_mode == 'card' && this.pos.config.iface_payment_terminal) {
                return true;
            }
            else {
                return false;
            }
        },
    });

    devices.ProxyDevice.include({
        wait_terminal_answer: function(cashregister) {
            if (this.pos.config.iface_payment_terminal_return) {
                return true;
            }
            return false;
        },
        get_data_send: function(order, line, currency_iso) {
            var data = {
                    'amount' : order.get_due(line),
                    'currency_iso' : currency_iso,
                    'payment_mode' : line.cashregister.journal.payment_mode,
                    'wait_terminal_answer' : this.wait_terminal_answer(),
                    };
            return data;
        },

        payment_terminal_transaction_start: function(screen, currency_iso){
            var self = this;
            var order = this.pos.get_order();
            var line = order.selected_paymentline;
            var data = self.get_data_send(order, line, currency_iso);
            if (this.wait_terminal_answer()) {
                this.message('payment_terminal_transaction_start_with_return', {'payment_info' : JSON.stringify(data)}).then(function (answer) {
                    if (answer) {
                        var transaction_result = answer['transaction_result'];
                        if (transaction_result == '7') {
                            // This means that the operation was not finished
                            // TODO : check what to do here. But I think this should do nothing.
                            screen.transaction_error();
                        } else if (transaction_result == '0') {
                            // This means that the operation was a success
                            // We get amount and set the amount in this line
                            var amount_in = answer['amount_msg'] / 100;
                            if (!amount_in == 0) {
                                line.set_amount(amount_in);
                                screen.order_changes();
                                screen.render_paymentlines();
                                var amount_in_formatted = screen.format_currency_no_symbol(amount_in);
                                screen.$('.paymentline.selected .edit').text(amount_in_formatted);
                                screen.$('.delete-button').css('display', 'none');
                                screen.$('.automatic-cashdrawer-transaction-start').css('display', 'none');
                            }
                        }
                    } else {
                        screen.transaction_error();
                    }
                });
            } else {
                this.message('payment_terminal_transaction_start', {'payment_info' : JSON.stringify(data)});
            }
        },
    });

    screens.PaymentScreenWidget.include({
        click_paymentmethods: function(id) {
            var self = this;
            this._super.apply(this, arguments);
            var line = this.pos.get_order().selected_paymentline;
            var auto = line.get_automatic_payment_terminal();
            if (auto) {
                this.pos.proxy.payment_terminal_transaction_start(self, self.pos.currency.name);
            }
        },
        transaction_error: function() {
            this.gui.show_popup('error',{
                'title': _t('Transaction error'),
                'body':  _t('Please, try it again.'),
                });
            return;
        },
    });

});
