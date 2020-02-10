/*
    POS Automatic Cashdrawer module for Odoo
    Copyright (C) 2016 Aurélien DUMAINE
    Copyright (C) 2019 Iván Todorovich (https://www.druidoo.io)
    @author: Aurélien DUMAINE
    The licence is in the file __openerp__.py
*/

odoo.define('pos_automatic_cashdrawer.models', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var Model = require('web.DataModel');

    models.load_fields("account.journal", [
        'payment_mode',
        'iface_automatic_cashdrawer',
    ]);

    models.load_fields("pos.config", [
        'iface_automatic_cashdrawer',
        'iface_automatic_cashdrawer_ip_address',
        'iface_automatic_cashdrawer_tcp_port',
        'group_pos_automatic_cashlogy_config',
    ]);

    var Session = new Model('pos.session');

    /*
        PosModel
    */
    var _super_PosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        // Overload 'set_cashier' function to display correctly
        // unauthorized function after cashier changed
        set_cashier: function(user) {
            this.gui.display_access_right_cashlogy(user);
            return _super_PosModel.set_cashier.apply(this, arguments);
        },

        // If the user is just checking automatic cashdrawer, then the system will try to connect proxy.
        after_load_server_data: function(session, attributes) {
            if (this.config.iface_automatic_cashdrawer) {
                this.config.use_proxy = true;
            }
            return _super_PosModel.after_load_server_data.apply(this, arguments);
        },

        // Checks if the opening balance is missing, fails silently
        check_opening_balance_missing: function() {
            var done = new $.Deferred();
            Session.call('check_opening_balance_missing', [this.pos_session.id])
            .then(function(res) { done.resolve(res); })
            .fail(function(error) {
                self.pos.gui.show_popup('error-traceback', {
                    'title': _t('Set balance error: ') + error.data.message,
                    'body': error.data.debug,
                });
            })
            return done;
        },

        // Sets the balance
        action_set_balance: function(inventory, balance) {
            var self = this;
            var done = Session.call('action_set_balance', [this.pos_session.id], {
                'inventory': inventory,
                'balance': balance,
            });
            done.fail(function(error) {
                self.pos.gui.show_popup('error-traceback', {
                    'title': _t('Set balance error: ') + error.data.message,
                    'body': error.data.debug
                });
            });
            return done;
        },

        // Checks if the session is able to do cash operations
        check_cash_in_out_possible: function() {
            return Session.call('check_cash_in_out_possible', [this.pos_session.id]);
        },

        // Saves cash in
        action_put_money_in: function(amount, reason) {
            if (!amount) { return $.Deferred().resolve(); }
            return Session.call('action_put_money_in', [this.pos_session.id], {
                'amount': amount,
                'reason': reason,
            });
        },

        action_take_money_out: function(amount, reason) {
            if (!amount) { return $.Deferred().resolve(); }
            return Session.call('action_take_money_out', [this.pos_session.id], {
                'amount': amount,
                'reason': reason,
            });
        },
    });

    /*
        Paymentline
    */
    var _super_Paymentline = models.Paymentline.prototype;
    models.Paymentline = models.Paymentline.extend({
        get_automatic_cashdrawer: function() {
            return this.cashregister.journal.iface_automatic_cashdrawer;
        },
    });

    return models;
});
