/*
    POS Automatic Cashdrawer module for Odoo
    Copyright (C) 2016 Aurélien DUMAINE
    Copyright (C) 2019 Iván Todorovich (https://www.druidoo.io)
    @author: Aurélien DUMAINE
    The licence is in the file __openerp__.py
*/

odoo.define('pos_automatic_cashdrawer.widgets', function (require) {
    "use strict";

    var PopupWidget = require('point_of_sale.popups');
    var screens = require('point_of_sale.screens');
    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var framework = require('web.framework');

    var _t = core._t;
    var QWeb = core.qweb;

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
                    'widget': AutomaticCashdrawerConfigWidget,
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
                    if (automatic_cashdrawer == 'connecting') {
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Automatic Cashdrawer Connecting..');
                    } else if (automatic_cashdrawer != 'connected') {
                        warning = true;
                        msg = msg ? msg + ' & ' : msg;
                        msg += _t('Automatic Cashdrawer Offline');
                    }
                }
                this.set_status(warning ? 'warning' : current_status, msg);
            }
        },
    });

    /*
        Cashdrawer configuration widget
    */
    var AutomaticCashdrawerConfigWidget = chrome.StatusWidget.extend({
        template: 'AutomaticCashdrawerConfigWidget',
        start: function(){
            var self = this;
            this.$el.click(function(){
                //self.pos.proxy.automatic_cashdrawer_connection_display_backoffice();
                self.gui.show_popup('cashdrawer_admin');
            });
        },
    });

    var AutomaticCashdrawerAdminDialog = PopupWidget.extend({
        template: 'AutomaticCashdrawerAdminDialog',

        show: function(options) {
            var self = this;
            this._super.apply(this, arguments);
            this.$('.actions .button').on('click', function(el) {
                self.gui.close_popup();
                var action = this.dataset['action'];
                if (action) {
                    self.action_handler(action);
                }
            });
        },

        action_handler: function(action) {
            var self = this;
            if (this['action_' + action]) {
                this['action_' + action].apply(this);
            } else {
                console.error('Unrecognized action', action);
            }
        },

        action_print_inventory: function() {
            var self = this;
            return this.pos.proxy.automatic_cashdrawer_get_inventory().then(function(res) {
                console.log('Cashdrawer Inventory:', res);
                self.pos.proxy.automatic_cashdrawer_print_inventory();
            });
        },

        action_display_backoffice: function() {
            var self = this;
            this.pos.proxy.automatic_cashdrawer_display_backoffice();
        },

        action_put_money_in: function() {
            var self = this;
            this.pos.check_cash_in_out_possible()
            .fail(function(error) {
                console.error(error);
                self.gui.close_popup()
                self.gui.show_popup('error', {
                    title: _t('Cash In/Out not possible'),
                    body: error.data.message,
                });
            }).then(function() {
                self.gui.show_popup('cashdrawer_cash_in');
            });
        },

        action_take_money_out: function() {
            var self = this;
            this.pos.check_cash_in_out_possible()
            .fail(function(error) {
                console.error(error);
                self.gui.close_popup()
                self.gui.show_popup('error', {
                    title: _t('Cash In/Out not possible'),
                    body: error.data.message,
                });
            }).then(function() {
                self.gui.show_popup('number', {
                    title: 'Cash Withdrawal',
                    body: 'How much do you want to withdraw?',
                    confirm: function(value) {
                        value = Number(value);
                        framework.blockUI();
                        self.pos.proxy.automatic_cashdrawer_dispense(value)
                        .then(function(res) {
                            self.pos.action_take_money_out(res, _t('Manual: take money out'))
                            if (res != value) {
                                self.gui.show_popup('error', {
                                    title: _t('Could not dispense the value requested'),
                                    body: (
                                        _t('The requested amount to dispense was: ') + value
                                        + '<br/>' +
                                        _t('The dispensed amount was: ') + res
                                    )
                                });
                            }
                        }).always(function() {
                            framework.unblockUI();
                        });
                    },
                });
            });
        },

        action_cancel: function() {
            this.pos.proxy.automatic_cashdrawer_stop_acceptance()
            .then(function(res) {
                console.log('Accepted: ', res);
            });
        },

        action_close_till: function() {
            var self = this;
            this.pos.check_cash_in_out_possible().fail(function(error) {
                console.error(error);
                self.gui.close_popup()
                self.gui.show_popup('error', {
                    title: _t('Cash In/Out not possible'),
                    body: error.data.message,
                });
            }).then(function() {
                self.pos.proxy.automatic_cashdrawer_display_close_till().then(function(res) {
                    if (res['added']) {
                        self.pos.action_put_money_in(res['added'], _t('Automatic Cashdrawer: Close Till / ADDED'));
                    }
                    if (res['dispensed']) {
                        self.pos.action_take_money_out(res['dispensed'], _t('Automatic Cashdrawer: Close Till / DISPENSED'));
                    }
                });
            });
        },

        action_empty_stacker: function() {
            var self = this;
            this.pos.check_cash_in_out_possible().fail(function(error) {
                console.error(error);
                self.gui.close_popup()
                self.gui.show_popup('error', {
                    title: _t('Cash In/Out not possible'),
                    body: error.data.message,
                });
            }).then(function() {
                self.pos.proxy.automatic_cashdrawer_display_empty_stacker().then(function(res) {
                    if (res) {
                        self.pos.action_take_money_out(res, _t('Automatic Cashdrawer: Empty Stacker'));
                    }
                });
            });
        },

        action_complete_emptying: function() {
            var self = this;
            this.pos.check_cash_in_out_possible().fail(function(error) {
                console.error(error);
                self.gui.close_popup()
                self.gui.show_popup('error', {
                    title: _t('Cash In/Out not possible'),
                    body: error.data.message,
                });
            }).then(function() {
                self.pos.proxy.automatic_cashdrawer_display_complete_emptying().then(function(res) {
                    if (res) {
                        self.pos.action_take_money_out(res, _t('Automatic Cashdrawer: Complete Emptying'));
                    }
                });
            });
        },

    });


    var AutomaticCashDrawerCashInDialog = PopupWidget.extend({
        template: 'AutomaticCashdrawerCashInDialog',
        
        show: function(options) {
            var self = this;
            this._super.apply(this, arguments);
            this.inputbuffer = 0.00;
            
            framework.blockUI();
            this.pos.proxy.automatic_cashdrawer_start_add_change()
            .then(function(res) {
                self.update_counter();
            }).fail(function(err) {
                self.close();
            }).always(function() {
                framework.unblockUI();
            });
        },

        close: function(options) {
            if (this.timer) { clearTimeout(this.timer); }
            this._super.apply(this, arguments);
        },

        update_counter: function() {
            var self = this;
            this.pos.proxy.automatic_cashdrawer_get_amount_accepted()
            .then(function(res) {
                console.log('Update counter', res);
                self.inputbuffer = res;
                self.$('.value').text(self.format_currency(self.inputbuffer));
                self.timer = setTimeout(function() { self.update_counter(); }, 500);
            });
        },

        click_confirm: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.pos.proxy.automatic_cashdrawer_stop_acceptance()
            .then(function(res) {
                self.pos.action_put_money_in(res, _t('Manual: put money in'));
            });
        },

        /*
            TODO: shuold return the money inserted (maybe)
            So, basically, we confirm the operation to the machine, and then we dispense
            the inserted amount.
        */
        click_cancel: function() {
            this.gui.show_popup('error', { message: 'Not implemented yet' });
            this._super.apply(this, arguments);
        },
    })


    gui.define_popup({name:'cashdrawer_admin', widget: AutomaticCashdrawerAdminDialog});
    gui.define_popup({name:'cashdrawer_cash_in', widget: AutomaticCashDrawerCashInDialog});

    return {
        AutomaticCashdrawerConfigWidget: AutomaticCashdrawerConfigWidget,
        AutomaticCashdrawerAdminDialog: AutomaticCashdrawerAdminDialog,
        AutomaticCashDrawerCashInDialog: AutomaticCashDrawerCashInDialog,
    };

});
