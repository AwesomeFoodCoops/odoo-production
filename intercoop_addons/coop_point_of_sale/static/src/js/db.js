odoo.define('coop_point_of_sale.db', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB');

    // Overide _product_search_string, search_product_in_category to allow searching product with accents
    PosDB.include({
        get_diacritics_search: function () {
            if (window.posmodel.config.hasOwnProperty("diacritics_insensitive_search")) {
                return window.posmodel.config.diacritics_insensitive_search;
            } else {
                return false;
            }
        },
        _product_search_string: function (product) {
            if (this.get_diacritics_search()) {
                // remove accents and not impact original product
                var clone_product = _.clone(product);
                clone_product.display_name = Diacritics.replace(clone_product.display_name);
                return this._super(clone_product);
            } else {
                return this._super(product);
            }
        },
        search_product_in_category: function (category_id, query) {
            if (this.get_diacritics_search()) {
                var removed_accents_query = Diacritics.replace(query);
                return this._super(category_id, removed_accents_query);
            } else {
                return this._super(category_id, query);
            }
        }
    });

});
