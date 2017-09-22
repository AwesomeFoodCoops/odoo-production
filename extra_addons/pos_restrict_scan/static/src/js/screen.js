/*
Copyright (C) 2016-Today: La Louve (<http://www.cooplalouve.fr>)
@author: La Louve
License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/

odoo.define('pos_restrict_scan.screen_custom', function (require) {
    "use strict";

    var screens = require('point_of_sale.screens');
    var gui = require('point_of_sale.gui');
    var core = require('web.core');
    var _t = core._t;

    /* ********************************************************
    Customize screens.ScreenWidget
    ******************************************************** */
    screens.ScreenWidget.include({

        // Modify barcode_product_action to prevent scanning product in
        // Payment Screen
        barcode_product_action: function(code){
            var self = this;
            if (self.gui.get_current_screen() != 'products'){
                this.gui.show_popup('error',{
                    'title': _t('Action Restricted!'),
                    'body':  _t('Product Scanning is only allowed on the products screen'),
                });
            } else {
                return self._super(code);
            }
        },
    });
});
