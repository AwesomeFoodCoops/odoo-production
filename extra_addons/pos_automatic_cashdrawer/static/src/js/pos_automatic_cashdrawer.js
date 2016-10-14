/*
    POS Automatic Cashdrawer module for Odoo
    Copyright (C) 2016 Aurélien DUMAINE
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
    var _t = core._t;
    var QWeb = core.qweb;

    models.load_fields("account.journal", ['payment_mode',
                                           'iface_automatic_cashdrawer']);
    models.load_fields("pos.config", ['iface_automatic_cashdrawer',
                                      'iface_automatic_cashdrawer_ip_address',
                                      'iface_automatic_cashdrawer_tcp_port',
                                      'iface_automatic_cashdrawer_display_accept_button',
                                      'iface_automatic_cashdrawer_screen_on_top'
                                      ]);

    // If the user is just checking automatic cashdrawer, then the system will try to connect proxy.
    var after_load_server_data_original = models.PosModel.prototype.after_load_server_data;
    models.PosModel = models.PosModel.extend({
        after_load_server_data: function(session, attributes) {
            if (this.config.iface_automatic_cashdrawer) {
                this.config.use_proxy = true;
            }
            return after_load_server_data_original.call(this);
        },
    });

    models.Paymentline = models.Paymentline.extend({
        get_automatic_cashdrawer: function() {
            return this.cashregister.journal.iface_automatic_cashdrawer;
        },
    });

    devices.ProxyDevice.include({
        init: function(){
            this._super.apply(this, arguments);
            this.set('cashdrawer_status', {});
            this.set_connection_cashdrawer_status('disconnected');
        },
        set_connection_cashdrawer_status: function(cashdrawer_status, drivers){
            var oldstatus = this.get('cashdrawer_status');
            var newstatus = {};
            newstatus.cashdrawer_status = cashdrawer_status;
            newstatus.drivers = cashdrawer_status === 'disconnected' ? {} : oldstatus.drivers;
            newstatus.drivers = drivers ? drivers : newstatus.drivers;
            this.set('cashdrawer_status', newstatus);
        },
        automatic_cashdrawer_transaction_start: function(screen) {
            var order = this.pos.get_order();
            var line = order.selected_paymentline;
            if (line) {
                var data = {
                        'amount': order.get_due(line),
                        'display_accept_button': this.pos.config.iface_automatic_cashdrawer_display_accept_button,
                        'screen_on_top': this.pos.config.iface_automatic_cashdrawer_screen_on_top
                        };
                this.message('automatic_cashdrawer_transaction_start', {'payment_info' : JSON.stringify(data)}).then(function (answer) {
                    // Check if there was any error or a value
                    var answer_info = answer['info'];
                    if (answer_info) {
                        var answer_type_expression = /[a-zA-Z]+/g;
                        var answer_type = answer_info.match(answer_type_expression);
                        if (answer_type) {
                            // If there is an answer type
                            if (answer_type[0] == "WR" && answer_type[1] == "CANCEL") {
                                // Case #WR:CANCEL#b#c#d#e# :
                                // TODO : check what to do here. But I think this should do nothing.
                            }
                            else if (answer_type[0] == "ER" && answer_type[1] == "BUSY") {
                                // Case #ER:BUSY# : answer_type[0] == "ER"
                                // TODO : check what to do here. But I think this wont append because the cash drawer wont give back this error.
                            }
                            else if (answer_type[0] == "ER") {
                                // Case #ER:xxxx#b#c#d#e# : answer_type[0] == "ER"
                                // TODO : check what to do here. But I think this wont append because the cash drawer wont give back this error.
                            }
                            else if (answer_type[0] == "WR" && answer_type[1] == "LEVEL") {
                                // Case #WR:LEVEL#b#c#d#e#:
                                // The return says that an amount was correctly given to the cache machine
                                var amount_expression = /[0-9]+/g;
                                var amount_expression = answer_info.match(amount_expression);
                                var amount_in = amount_expression[0] / 100;
                                var amount_out = amount_expression[1] / 100;
                                if (!amount_in == 0) {
                                    // TODO : Check the amount_out and what is display on screen ?
                                    line.set_amount(amount_in);
                                    screen.order_changes();
                                    screen.render_paymentlines();
                                    var amount_in_formatted = screen.format_currency_no_symbol(amount_in);
                                    screen.$('.paymentline.selected .edit').text(amount_in_formatted);
                                    screen.$('.delete-button').css('display', 'none');
                                    screen.$('.automatic-cashdrawer-transaction-start').css('display', 'none');
                                }
                            }
                        }
                    }
                });
            }
            // TODO : this function should check the real amount received, and correct it / handle warnings and errors sent from the cashdrawer
        },
        automatic_cashdrawer_connection_check: function(){
            // call this function on POS loading to be able to know if the machine is available
            var data = {
                    'ip_address': this.pos.config.iface_automatic_cashdrawer_ip_address,
                    'tcp_port': this.pos.config.iface_automatic_cashdrawer_tcp_port
                    }
            var self = this;
            self.message('automatic_cashdrawer_connection_check', {'connection_info' : JSON.stringify(data)});
        },
        automatic_cashdrawer_connection_init: function(){
            // TODO : call this function on POS loading
            // TODO : only managers should be able to see/clic this button
            var data = {
                    'ip_address': this.pos.config.iface_automatic_cashdrawer_ip_address,
                    'tcp_port': this.pos.config.iface_automatic_cashdrawer_tcp_port
                    }
            this.message('automatic_cashdrawer_connection_init', {'connection_info' : JSON.stringify(data)}).then(function(answer) {
                console.log(answer);
            });
        },
        automatic_cashdrawer_connection_exit: function(){
            // TODO : call this function on POS exit
            // TODO : only managers should  be able to see/clic this button
            this.message('automatic_cashdrawer_connection_exit').then(function(answer) {
                console.log(answer);
            });
        },
        automatic_cashdrawer_connection_display_backoffice: function(){
            // TODO : only managers should  be able to see/clic this button
            var data = {'bo' : 'null'}
            this.message('automatic_cashdrawer_display_backoffice', {'backoffice_info' : JSON.stringify(data)}).then(function(answer) {
                console.log(answer);
            });
        },
    });

    screens.PaymentScreenWidget.include({
        is_manager: function () {
            if (this.pos) {
                var user = this.pos.get_cashier();
                if (user.role === 'manager') {
                    return true;
                }
            }
            return false;
        },
//            render_paymentlines : function(){
//                this._super.apply(this, arguments);
//                var self = this;
//                        // Directly call the automatic cashdrawer if the journal is checked
////                  self.pos.proxy.automatic_cashdrawer_transaction_start($(this).data('cid'), self);
//                this.$('.paymentlines-container').unbind('click').on('click','.automatic-cashdrawer-transaction-start', function(event){
//                // Why this "on" thing links several time the button to the action if I don't use "unlink" to reset the button links before ?
//                            //console.log(event.target);
//                    self.pos.proxy.automatic_cashdrawer_transaction_start($(this).data('cid'), self);
//                });
//            },
        click_paymentmethods: function(id) {
            this._super.apply(this, arguments);
            var line = this.pos.get_order().selected_paymentline;
            var auto = line.get_automatic_cashdrawer();
            if (auto) {
                this.pos.proxy.automatic_cashdrawer_transaction_start(this);
            }
        },

        renderElement : function() {
            this._super.apply(this, arguments);
            var self = this;
            this.$('.automatic-cashdrawer-connection-init').click(function() {
                self.pos.proxy.automatic_cashdrawer_connection_init();
            });
            this.$('.automatic-cashdrawer-connection-exit').click(function() {
                self.pos.proxy.automatic_cashdrawer_connection_exit();
            });
            this.$('.automatic-cashdrawer-display-backoffice').click(function() {
                self.pos.proxy.automatic_cashdrawer_connection_display_backoffice();
            });
        },
    });

    /* ------- Uncomment init method bellow to be able to get auto cashdrawer widget------- */
    chrome.Chrome.include({
//        init: function() {
//            this._super.apply(this, arguments);
//            this.add_autocashdrawerwidget();
//        },
        add_autocashdrawerwidget: function () {
            var native_widgets = this.widgets;
            var autocashdrawerwidget = {
                    'name':   'auto_cashdrawer_status',
                    'widget': AutoCashdrawerWidget,
                    'append':  '.pos-rightheader',
                    'condition': function(){ return this.pos.config.iface_automatic_cashdrawer; },
                }
            var sorted_widgets = []
            for (var i = 0, len = native_widgets.length; i < len; i++) {
                sorted_widgets.push(native_widgets[i]);
                if (native_widgets[i].name === 'order_selector') {
                    sorted_widgets.push(autocashdrawerwidget);
                }
            }
            this.widgets = sorted_widgets;
        }
    });

    /* ------- Synch. automatic cashdrawer Status ------- */
    // Displays if the automatic cashdrawer is not initialized
    var AutoCashdrawerWidget = chrome.StatusWidget.extend({
         template: 'AutoCashdrawerWidget',
         cashdrawer_status: ['connected',
                             'connecting',
                             'initialized',
                             'disconnected',
                             'warning',
                             'error'],
         set_cashdrawer_status: function(cashdrawer_status, msg){
             for(var i = 0; i < this.cashdrawer_status.length; i++){
                 this.$('.js_'+this.cashdrawer_status[i]).addClass('oe_hidden');
             }
             this.$('.js_'+cashdrawer_status).removeClass('oe_hidden');
             
             if(msg){
                 this.$('.js_msg').removeClass('oe_hidden').html(msg);
             }else{
                 this.$('.js_msg').addClass('oe_hidden').html('');
             }
         },
         set_smart_cashdrawer_status: function(cashdrawer_status) {
             if (cashdrawer_status.cashdrawer_status === 'connected'){
                 var warning = false;
                 var msg = '';
                 if (this.pos.config.iface_automatic_cashdrawer) {
                     var automatic_cashdrawer = cashdrawer_status.drivers.automatic_cashdrawer ? cashdrawer_status.drivers.automatic_cashdrawer.status : false;
                     if( automatic_cashdrawer != 'connected' && automatic_cashdrawer != 'connecting'){
                         warning = true;
                         msg += _t('Automatic cashdrawer');
                     }
                 }
                 msg = msg ? msg + ' ' + _t('Offline') : msg;
                 this.set_cashdrawer_status(warning ? 'warning' : 'connected', msg);
             } else {
                 this.set_cashdrawer_status(cashdrawer_status.cashdrawer_status, {});
             }
         },
         start: function(){
             var self = this;
             this.set_smart_cashdrawer_status(this.pos.proxy.get('cashdrawer_status'));
             this.$el.click(function(){
                 // TODO: improve this !
                 self.set_cashdrawer_status('connecting', {});
                 self.pos.proxy.automatic_cashdrawer_connection_check();
                 self.set_cashdrawer_status('connected', {});
             });
         },
    });
});
