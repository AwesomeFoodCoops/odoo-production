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
    var PopupWidget = require('point_of_sale.popups');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;

    models.load_fields("account.journal", ['payment_mode']);

    var _paylineproto = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        get_automatic_payment_terminal: function() {
            if (this.cashregister.journal.payment_mode == 'card' && this.pos.config.iface_payment_terminal) {
                return true;
            }
            else {
                return false;
            }
        },
        set_tpe_return_message: function(value) {
            this.order.assert_editable();
            this.tpe_return_message = value;
            this.trigger('change', this);
        },
        get_tpe_return_message: function() {
            return this.tpe_return_message;
        },
        export_as_JSON: function(){
            return _.extend(_paylineproto.export_as_JSON.apply(this, arguments), {
                tpe_return_message: this.get_tpe_return_message(),
            });
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
                screen.waiting_for_tpe_return();
                var amount = line.get_amount()
                this.message('payment_terminal_transaction_start_with_return', {'payment_info' : JSON.stringify(data)}).then(function (answer) {
                    screen.close_waiting_for_tpe_return();
                    if (answer) {
                        var transaction_result = answer['transaction_result'];
                        if (transaction_result == '7') { // not finished transaction (cancelled, error, etc.)
                            // This means that the operation was not finished
                            // TODO : check what to do here. But I think this should do nothing.
                            screen.transaction_error();
                        } else if (transaction_result == '0') { // transaction accepted
                            if (amount == 0) {
                                order.remove_paymentline(line);
                                screen.reset_input();
                                screen.render_paymentlines();
                            }
                        } else if (transaction_result == '0') {
                            // This means that the operation was a success
                            // We get amount and set the amount in this line
                            var amount_in = answer['amount_msg'] / 100;
                            if (!amount_in == 0) {
                                line.set_amount(amount_in);
                                line.set_tpe_return_message(answer['tpe_return_message']);
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
                        if (amount == 0) {
                            order.remove_paymentline(line);
                            screen.reset_input();
                            screen.render_paymentlines();
                        }
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
        waiting_for_tpe_return: function() {
            this.gui.show_popup('waitingfortpereturn',{
                'title': _t('Transaction in progress'),
                'body':  _t('Please, wait until TPE return.'),
                });
            return;
        },
        close_waiting_for_tpe_return: function() {
            this.gui.close_popup('waitingfortpereturn');
            return;
        },
    });

    // Popup to show all transaction state for the payment.

    var WaitingForTPEReturnPopupWidget = PopupWidget.extend({
        template: 'WaitingForTPEReturnPopupWidget',
        show: function (options) {
            var self = this;
            this._super(options);
        }
    });

    gui.define_popup({name:'waitingfortpereturn', widget: WaitingForTPEReturnPopupWidget});
});
