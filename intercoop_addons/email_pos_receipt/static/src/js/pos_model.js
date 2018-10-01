/*
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/


odoo.define('email_pos_receipt.pos_model', function (require) {
    "use strict";

    var pos_model = require('point_of_sale.models');
    pos_model.load_fields("res.partner", "email_pos_receipt");
    pos_model.load_models([{
        model: "pos.config.settings",
        fields: ["receipt_options"],
        loaded: function(self, config_settings){
            const config_setting = config_settings.length > 0 ? config_settings.reduce(function(prev, current) {
                return (prev.id > current.id) ? prev : current
            }) : false; //returns object
            self.config_settings = config_setting;
        }
    }]);

});
