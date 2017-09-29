/*
Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
@author: Sylvain LE GAL (https://twitter.com/legalsylvain)
License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
*/


odoo.define('coop_point_of_sale.coop_point_of_sale', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    var screens = require('point_of_sale.screens');
    var core = require('web.core');
    var gui = require('point_of_sale.gui');
    var _t = core._t;

/* ********************************************************
Overload models.PosModel
******************************************************** */
    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function (session, attributes) {
            var partner_model = _.find(this.models, function(model){ return model.model === 'res.partner'; });
            partner_model.fields.push('barcode_base');
            partner_model.fields.push('cooperative_state');
            return _super_posmodel.initialize.apply(this, arguments);
        },
    });

});
