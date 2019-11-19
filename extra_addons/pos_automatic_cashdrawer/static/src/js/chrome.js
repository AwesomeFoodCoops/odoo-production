/*
    POS Automatic Cashdrawer module for Odoo
    Copyright (C) 2019 Iván Todorovich (https://www.druidoo.io)
    The licence is in the file __openerp__.py
*/

odoo.define('pos_automatic_cashdrawer.chrome', function (require) {
    "use strict";

    var chrome = require('point_of_sale.chrome');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var framework = require('web.framework');

    var _t = core._t;
    var QWeb = core.qweb;

    chrome.Chrome.include({

        /*
            Extend init to display an open session balance message
            It will check if the session has an opening balance cashbox and
            if it doesn't, it will ask the user if he wants to synchronize it with
            the automatic cashdrawer
        */
        init: function() {
            var self = this;
            this._super.apply(this, arguments);
            this.ready.done(function() {
                if (self.pos.config.iface_automatic_cashdrawer) {
                    self.pos.check_opening_balance_missing().then(function(missing) {
                        if (!missing) return;
                        self.gui.show_popup('confirm', {
                            title: _t('Sync Opening Balance'),
                            body: _t('The opening balance for this session is missing. Do you wan\'t to synchronize it with the automatic cashdrawer?'),
                            confirm: function() {
                                framework.blockUI();
                                var done = self.pos.proxy.automatic_cashdrawer_get_inventory();
                                done.then(function(inventory) {
                                    self.pos.action_set_balance(inventory.total, 'start').then(function() {
                                        self.gui.show_popup('alert', {
                                            title: _t('Opening Balance Synchronized'),
                                            body: _t('The opening balance was synchronized successfully.'),
                                        });
                                    })
                                });
                                done.always(function() { framework.unblockUI(); });
                            }
                        })
                    })
                }
            });
        },

    });


    gui.Gui.include({

        /*
            Overload close so that we can synchronize the closing balance
        */
        close: function() {
            var self = this;
            var args = arguments;
            var _super = this._super;

            if (!this.pos.config.iface_automatic_cashdrawer) {
                return this._super.apply(this, arguments);
            }

            self.chrome.loading_show();
            self.chrome.loading_message(_t('Synchronizing automatic cashdrawer inventory'));
            self.pos.proxy.automatic_cashdrawer_get_inventory()
            .then(function(inventory) {
                self.pos.action_set_balance(inventory.total, 'end').then(function() {
                    _super.apply(self, args);
                });
            })
            .fail(function() {
                _super.apply(self, args);
            })
            .always(function() {
                self.chrome.loading_hide();
            });
        },

    });

    return {
        chrome: chrome.Chrome,
        gui: gui.Gui,
    }
});
