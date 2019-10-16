/*
    POS Automatic Cashdrawer module for Odoo
    Copyright (C) 2016 Aurélien DUMAINE
    Copyright (C) 2019 Iván Todorovich (https://www.druidoo.io)
    @author: Aurélien DUMAINE
    The licence is in the file __openerp__.py
*/

odoo.define('pos_automatic_cashdrawer.pos_automatic_cashdrawer', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var devices = require('point_of_sale.devices');
    var models = require('point_of_sale.models');
    var core = require('web.core');
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');

    var _t = core._t;
    var QWeb = core.qweb;

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

    // Overload 'set_cashier' function to display correctly
    // unauthorized function after cashier changed
    var _set_cashier_ = models.PosModel.prototype.set_cashier;
    models.PosModel.prototype.set_cashier = function(user){
        this.gui.display_access_right_cashlogy(user);
        _set_cashier_.call(this, user);
    };

    // If the user is just checking automatic cashdrawer, then the system will try to connect proxy.
    var _after_load_server_data = models.PosModel.prototype.after_load_server_data;
    models.PosModel = models.PosModel.extend({
        after_load_server_data: function(session, attributes) {
            if (this.config.iface_automatic_cashdrawer) {
                this.config.use_proxy = true;
            }
            return _after_load_server_data.call(this);
        },
    });

    models.Paymentline = models.Paymentline.extend({
        get_automatic_cashdrawer: function() {
            return this.cashregister.journal.iface_automatic_cashdrawer;
        },
    });

    // Show or hide the cashdrawer backend feature
    // TODO: Move this to pos_automatic_cashdrawer_cashlogy
    gui.Gui.prototype.display_access_right_cashlogy = function(user){
        if (user.groups_id.indexOf(this.pos.config.group_pos_automatic_cashlogy_config[0]) != -1) {
            $('.js_auto_cashdrawer_config').removeClass('oe_hidden');
        } else {
            $('.js_auto_cashdrawer_config').addClass('oe_hidden');
        }
    };
    
    devices.ProxyDevice.include({

        /*
            Overload keepalive.
            This function is called right after the PosBox is connected and the handshake is made.
            Normally, it starts a keepalive timer that request /hw_proxy/status_json
            But we're also sending the Cashdrawer connection config here.
        */
        keepalive: function() {
            this._super.apply(this, arguments);
            console.log('DEBUG', 'keepalive called', this.pos.config);
            if (this.pos.config.iface_automatic_cashdrawer) {
                this.message('cashlogy/connect', {
                    'config': {
                        'host': this.pos.config.iface_automatic_cashdrawer_ip_address,
                        'port': this.pos.config.iface_automatic_cashdrawer_tcp_port
                    }
                });
            }
        },

        /*
            Starts a sale transaction using the backoffice.
            It will display the backoffice window so that the cashier can
            confirm the amount.
            It will return the collected amount.

            options.operation_number    default to 00000

            Possible exceptions:
                CancelledOperation
                Busy

            @returns    {amount: 0.00}
        */
        automatic_cashdrawer_transaction_start: function(amount, options) {
            options = options || {};
            return this.message('cashlogy/transaction_start', {
                'amount': amount,
                'options': options,
            });
        },

        /*
            Dispenses money
            amount              float
            options.only_coins  default False
        */
        automatic_cashdrawer_dispense: function(amount, options) {
            options = options || {};
            return this.message('cashlogy/dispense', {
                'amount': amount,
                'options': options,
            });
        },

        /*
            Start add change
            Used to load money into the cashdrawer
            It has to be stopped using stop_acceptance
            The amount loaded so far can be queried with get_amount_accepted
        */
        automatic_cashdrawer_start_add_change: function() {
            return this.message('cashlogy/start_add_change');
        },

        /*
            Returns the money accepted so far
            @returns 0.00
        */
        automatic_cashdrawer_get_amount_accepted: function() {
            return this.message('cashlogy/get_amount_accepted');
        },

        /*
            Stops acceptance of money
            @returns 0.00
        */
        automatic_cashdrawer_stop_acceptance: function() {
            return this.message('cashlogy/stop_acceptance');
        },

        /*
            Gets the inventory of the machine
            Returns {total: {}, recycler: {}, stacker: {}}
        */
        automatic_cashdrawer_get_inventory: function() {
            return this.message('cashlogy/get_inventory');
        },

        /*
            Prints the current inventory of the machine
        */
        automatic_cashdrawer_print_inventory: function() {
            return $.Deferred().reject('Not implemented yet. TODO');
        },

        /*
            Displays the backoffice panel.
            TODO: Move this to pos_automatic_cashdrawer_cashlogy, or somehow toggle this feature
            depending on a supported feature list.
        */
        automatic_cashdrawer_connection_display_backoffice: function(){
            // TODO : only managers should  be able to see/clic this button
            // Check for security group of current user
            if (!true) { return $.Deferred().reject(_t('AccessError')); }
            return this.message('cashlogy/display_backoffice');
        },

    });


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

        /*
            When the payment journal is clicked, we start the automatic_cashdrawer_transaction
        */
        click_paymentmethods: function (id) {
            this._super.apply(this, arguments);
            var self = this;
            var order = this.pos.get_order();
            var line = order.selected_paymentline;
            if (line && line.get_automatic_cashdrawer()) {
                var amount = order.get_due(line);
                // TODO Block input
                this.pos.proxy.automatic_cashdrawer_transaction_start(amount, {operation_number: order.name})
                .done(function(response) {
                    console.log('Response', response);
                    line.set_amount(response.amount);
                    self.order_changes();
                    self.render_paymentlines();
                    var amount_formatted = self.format_currency_no_symbol(response.amount);
                    self.$('.paymentline.selected .edit').text(amount_formatted);
                    self.$('.delete-button').css('display', 'none');
                })
            }
        },
    });


    /*
        Attach status widgets
    */
    chrome.Chrome.include({
        init: function() {
            this._super.apply(this, arguments);
            this.automatic_cashdrawer_add_widgets();
        },

        automatic_cashdrawer_add_widgets: function () {
            var native_widgets = this.widgets;
            var autocashdrawerconfigwidget = {
                    'name': 'auto_cashdrawer_config',
                    'widget': AutoCashdrawerConfigWidget,
                    'append': '.pos-rightheader',
                    'condition': function(){ return this.pos.config.iface_automatic_cashdrawer; },
            }
            var sorted_widgets = []
            for (var i = 0, len = native_widgets.length; i < len; i++) {
                sorted_widgets.push(native_widgets[i]);
                if (native_widgets[i].name === 'order_selector') {
                    sorted_widgets.push(autocashdrawerconfigwidget);
                }
            }
            this.widgets = sorted_widgets;
        }
    });


    /*
        Add Cashdrawer connection to the ProxyStatus widget
    */
    chrome.ProxyStatusWidget.include({
        set_smart_status: function (status) {
            var self = this;
            var res = this._super.apply(this, arguments);
            if (status.status === 'connected') {
                // Get the current status based on the css classes of the widget
                // Sadly, there's not a property to check this.
                var current_status;
                for(var i=0; i < this.status.length; i++) {
                    var _el = this.$('.js_' + this.status[i]);
                    if (_el.length && !_el.hasClass('oe_hidden')) {
                        current_status = this.status[i];
                    }
                }
                var warning = (current_status === 'warning');
                var msg = this.$('.js_msg').html();
                if (this.pos.config.iface_automatic_cashdrawer) {
                    var automatic_cashdrawer = status.drivers.automatic_cashdrawer ? status.drivers.automatic_cashdrawer.status : false;
                    if (automatic_cashdrawer != 'connected' && automatic_cashdrawer != 'connecting') {
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Automatic Cashdrawer Offline');
                    }
                }
                this.set_status(warning ? 'warning' : current_status, msg);
            }
        },
    });

    var AutoCashdrawerConfigWidget = chrome.StatusWidget.extend({
        template: 'AutoCashdrawerConfigWidget',
        start: function(){
            var self = this;
            this.$el.click(function(){
                self.pos.proxy.automatic_cashdrawer_connection_display_backoffice();
            });
        },
    });

    return {
        AutoCashdrawerConfigWidget: AutoCashdrawerConfigWidget,
    };

});
