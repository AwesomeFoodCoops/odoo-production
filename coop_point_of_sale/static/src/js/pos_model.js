/*
# Copyright (C) 2016-Today: La Louve (<http://www.lalouve.fr/>)
# Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
# @author: La Louve
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html
*/


odoo.define('coop_point_of_sale.pos_model', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var pos_model = require('point_of_sale.models');
    pos_model.load_models([{
        model: "pos.config",
        fields: ["account_journal_ids", "payable_to"],
        loaded: function(self, config_info_settings){
            const config_setting = config_info_settings.length > 0 ? config_info_settings.reduce(function(prev, current) {
                return (prev.id > current.id) ? prev : current
            }) : false; //returns object
            self.config_info_settings = config_setting;
        }
    }]);
    pos_model.PosModel = pos_model.PosModel.extend({
        // reload the list of partner, returns as a deferred that resolves if there were
        // updated partners, and fails if not
        load_new_partners: function(){
            var self = this;
            var def  = new $.Deferred();
            var fields = _.find(this.models,function(model){ return model.model === 'res.partner'; }).fields;
            var domain = [['customer','=',true], ['is_deceased','=',false],['write_date','>',this.db.get_partner_write_date()]];
            rpc.query({
                    model: 'res.partner',
                    method: 'search_read',
                    args: [domain, fields],
                }, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function(partners){
                    if (self.db.add_partners(partners)) {   // check if the partners we got were real updates
                        def.resolve();
                    } else {
                        def.reject();
                    }
                }, function(type,err){ def.reject(); });
            return def;
        },
    });
    pos_model.load_domains = function(model_name, domain) {
        if (!(domain instanceof Array)) {
            domain = [domain];
        }
    
        var models = pos_model.PosModel.prototype.models;
        for (var i = 0; i < models.length; i++) {
            var model = models[i];
            if (model.model === model_name) {
                // if 'domains' is empty all domains are loaded, so we do not need
                // to modify the array
                if ((model.domain instanceof Array) && model.domain.length > 0) {
                    model.domain = model.domain.concat(domain || []);
                }
            }
        }
    };
    pos_model.load_domains('res.partner', [['is_deceased','=',false]])
});
