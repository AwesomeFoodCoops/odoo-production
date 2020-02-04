/*
    POS Automatic Validation module for Odoo
    Copyright (C) 2017 Julius Network Solutions
    @author: Mathieu VATEL
    The licence is in the file __openerp__.py
*/

odoo.define('pos_automatic_validation.pos_automatic_validation', function (require) {
    "use strict";
    var screens = require('point_of_sale.screens');
    var models = require('point_of_sale.models');

    models.load_fields("account.journal", ['iface_automatic_validation']);

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
