/* Copyright (C) 2020-Today: Druidoo (<https://www.druidoo.io>)
   License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('pos_order_wait_save.screens', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var PaymentScreenWidget = screens.PaymentScreenWidget;

    PaymentScreenWidget.include({
        finalize_validation: function () {
            var self = this;
            if (self.pos.config.order_wait_save_timeout == 0) {
                return this._super();
            }
            var new_timeout = self.pos.config.order_wait_save_timeout * 1000;
            var order = this.pos.get_order();
            if (order.is_paid_with_cash() && this.pos.config.iface_cashdrawer) {
                this.pos.proxy.open_cashbox();
            }
            order.initialize_validation_date();
            order.finalized = true;
            if (order.is_to_invoice()) {
                var invoiced = this.pos.push_and_invoice_order(order);
                this.invoicing = true;
                invoiced.fail( function () {
                    var pending = self.pos.db.get_orders().length;
                    if (pending) {
                        order.is_not_saved_yet = true;
                    }
                    order.is_not_saved_yet = true;
                });
                invoiced.fail(this._handleFailedPushForInvoice.bind(this, order, false));
                invoiced.done( function () {
                    self.invoicing = false;
                    self.gui.show_screen('receipt')
                });
            } else {
                var done_order = this.pos.push_order(order);
                done_order.done( function () {
                    var pending = self.pos.db.get_orders().length;
                    if (pending) {
                        order.is_not_saved_yet = true;
                    }
                    self.gui.show_screen('receipt');
                });
            }
        },
    });

});
