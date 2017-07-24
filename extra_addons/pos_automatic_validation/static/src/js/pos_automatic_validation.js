/*
    POS Automatic Validation module for Odoo
    Copyright (C) 2017 Julius Network Solutions
    @author: Mathieu VATEL
    The licence is in the file __openerp__.py
*/

odoo.define('pos_automatic_validation.pos_automatic_validation', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var devices = require('point_of_sale.devices');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var _t = core._t;
    var QWeb = core.qweb;

    models.load_fields("account.journal", ['payment_mode',
                                           'iface_automatic_validation']);

    models.Paymentline = models.Paymentline.extend({
        get_automatic_validation: function() {
            return this.cashregister.journal.iface_automatic_validation;
        },
    });

    screens.PaymentScreenWidget.include({
        render_paymentlines: function() {
            this._super();
            var self = this;
            var order = this.pos.get_order();
            if (order.is_paid()) {
                var selected_line = order.selected_paymentline;
                if (selected_line) {
                    var auto_validation = selected_line.get_automatic_validation();
                    if (auto_validation == true) {
                        self.validate_order();
                    }
                }
            }
        },
    });
    
});
