/*
    POS Automatic Cashdrawer module for Odoo
    Copyright (C) 2016 Aurélien DUMAINE
    Copyright (C) 2019 Iván Todorovich (https://www.druidoo.io)
    @author: Aurélien DUMAINE
    The licence is in the file __openerp__.py
*/

odoo.define('pos_automatic_cashdrawer.screens', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');

    var _t = core._t;
    var QWeb = core.qweb;

    /*
        Show or hide the cashdrawer backend feature
        TODO: Move this to pos_automatic_cashdrawer_cashlogy
    */
    gui.Gui.prototype.display_access_right_cashlogy = function(user){
        if (user.groups_id.indexOf(this.pos.config.group_pos_automatic_cashlogy_config[0]) != -1) {
            $('.js_auto_cashdrawer_config').removeClass('oe_hidden');
        } else {
            $('.js_auto_cashdrawer_config').addClass('oe_hidden');
        }
    };

    /*
        Overload 'start' function to display correctly unauthorized function
        at the beginning of the session, based on current user

        TODO: Analyze why we need this here, on the numpad..
        Isn't it already handled by the set_cashier function?
    */
    screens.NumpadWidget.include({
        start: function() {
            this._super();
            this.gui.display_access_right_cashlogy(this.pos.get_cashier());
        },
    });


    screens.PaymentScreenWidget.include({
        // When the payment journal is clicked, we start the automatic_cashdrawer_transaction
        click_paymentmethods: function (id) {
            this._super.apply(this, arguments);
            var self = this;
            var order = this.pos.get_order();
            var line = order.selected_paymentline;
            if (line && line.get_automatic_cashdrawer()) {
                var amount = order.get_due(line);
                // TODO Block input
                this.gui.show_popup('cashdrawer_cash_in', {
                    title: _t('Customer Transaction'),
                    to_collect: amount,
                    auto_accept: true,
                    allow_cancel: true,
                    confirm: function(amount, amount_in, amount_out) {
                        var amount_formatted = self.format_currency_no_symbol(amount_in);
                        line.set_amount(amount_in);
                        self.order_changes();
                        self.render_paymentlines();
                        self.$('.paymentline.selected .edit').text(amount_formatted);
                        self.$('.delete-button').css('display', 'none');
                    },
                    cancel: function() {
                        // Remove payment line
                        self.click_delete_paymentline(line.cid);
                    }
                })
            }
        },
    });

    return screens;
});
