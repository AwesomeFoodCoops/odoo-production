/*
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/

odoo.define('pos_receipt_by_email.receipt_screen_widget', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var _t = core._t;

    screens.ReceiptScreenWidget.include({

        print_web: function() {
            var client = this.pos.get_client();
            var email_pos_receipt = client ? client.email_pos_receipt: false;
            if (this.pos.config.is_print_receipt == false && email_pos_receipt){
                console.log("Skip print receipt by web")
                return
            } else {
                return this._super();
            }
        },

        print_xml: function() {
            var client = this.pos.get_client();
            var email_pos_receipt = client ? client.email_pos_receipt: false;
            if (this.pos.config.is_print_receipt == false && email_pos_receipt){
                console.log("Skip print receipt by xml")
                return
            }else{
                return this._super()
            }
        },
    });


});
