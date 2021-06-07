/*
Copyright (C) 2016-Today: La Louve (<http://www.lalouve.net/>)
Copyright (C) 2019-Today: Druidoo (<https://www.druidoo.io>)
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
        after_load_server_data: function(session, attributes) {
            // work-around because of issue in odoo code https://github.com/odoo/odoo/commit/e14ab697727d87773dbefba11453b9edca79fc68
            // this.cashier = self.get_cashier(); appears too early in loading models steps raise some data of cashier/user is missing
            // reset cashier again here to make sure it has sufficient data
            this.cashier = null;
            this.cashier = this.get_cashier();

            return _super_posmodel.after_load_server_data.call(this);
        },
    });

    // Orderline
    var _super_orderline = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        generate_wrapped_product_name: function() {
            // keep only the first line in long product names
            return _super_orderline.generate_wrapped_product_name.call(this).slice(0, 1);
        },
    });

    // Custom OrderWidget to remove order line when setting quantity equal to 0
    screens.OrderWidget.include({
        set_value: function(val) {
            var order = this.pos.get_order();
            var selectedLine = order.get_selected_orderline();
            if (selectedLine) {
                var mode = this.numpad_state.get('mode');
                if( mode === 'quantity'){
                    if (val == '0'){
                          order.remove_orderline(selectedLine);
                    }
                    else {
                        selectedLine.set_quantity(val);
                    }
                }else if( mode === 'discount'){
                    selectedLine.set_discount(val);
                }else if( mode === 'price'){
                    selectedLine.set_unit_price(val);
                }
            }
        },
    });

    //Merge louve_custom_pos module to coop_point_of_sale
    //remove louve_custom_pos from version 12
    screens.ClientListScreenWidget.include({
        partner_icon_url: function (id)  {
            return '/web/image?model=res.partner&id='+id+'&field=image';
        },
    });

    // Product to weight
    screens.ProductCategoriesWidget.include({
        perform_search: function(category, query, buy_result){
            var products;
            if(query){
                products = this.pos.db.search_product_in_category(category.id,query);
                if(buy_result && products.length === 1){
                        this.pos.get_order().add_product(products[0]);
                        this.clear_search();
                }
                else if (buy_result && products.length === 0){
                    this.pos.barcode_reader.scan(query);
                }
                else{
                    this.product_list_widget.set_product_list(products);
                }
            }else{
                products = this.pos.db.get_product_by_category(this.category.id);
                this.product_list_widget.set_product_list(products);
            }
        },
    
    });
});