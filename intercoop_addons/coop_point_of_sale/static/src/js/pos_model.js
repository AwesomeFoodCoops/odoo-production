/*
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/


odoo.define('coop_point_of_sale.pos_model', function (require) {
    "use strict";

    var pos_model = require('point_of_sale.models');
    pos_model.load_models([{
        model: "pos.config.settings",
        fields: ["account_journal_ids", "payable_to"],
        loaded: function(self, config_settings){
            const config_setting = config_settings.length > 0 ? config_settings.reduce(function(prev, current) {
                return (prev.id > current.id) ? prev : current
            }) : false; //returns object
            self.config_settings = config_setting;
        }
    }]);

});
