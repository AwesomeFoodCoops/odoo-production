odoo.define('pos_payment_terminal.devices', function (require) {
    "use strict";

    var devices = require('point_of_sale.devices');

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
                    'payment_mode' : line.cashregister.journal.pos_terminal_payment_mode,
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
                screen.$('.delete-button').css('display', 'none');
                this.message('payment_terminal_transaction_start_with_return', {'payment_info' : JSON.stringify(data)}, { timeout: 240000 }).then(function (answer) {
                    if (answer) {
                        var transaction_result = answer['transaction_result'];
                        if (transaction_result == '7') {
                            // This means that the operation was not finished
                            // TODO : check what to do here. But I think this should do nothing.
                            screen.transaction_error();
                            screen.$('.delete-button').css('display', 'block');
                            //$('.back').show();
                        } else if (transaction_result == '0') {
                            // This means that the operation was a success
                            // We get amount and set the amount in this line
                            var rounding = self.pos.currency.rounding;
                            var amount_in = round_pr(answer['amount_msg'] / 100, rounding);
                            //var amount_in = answer['amount_msg'] / 100;
                            if (!amount_in == 0) {
                                line.set_amount(amount_in);
                                if ('payment_terminal_return_message' in answer) {
                                    line.set_payment_terminal_return_message(answer.payment_terminal_return_message);
                                }
                                screen.order_changes();
                                screen.render_paymentlines();
                                var amount_in_formatted = screen.format_currency_no_symbol(amount_in);
                                screen.$('.paymentline.selected .edit').text(amount_in_formatted);
                                screen.$('.delete-button').css('display', 'none');
                                //screen.$('.automatic-cashdrawer-transaction-start').css('display', 'none');
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
});
