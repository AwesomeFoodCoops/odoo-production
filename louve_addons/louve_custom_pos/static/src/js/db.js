odoo.define('lalouve_custom_pos.db', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB');

    PosDB.include({
        // Overide _product_search_string to allow searching product by
        // Internal Reference and Barcode Only
        _product_search_string: function(product){
            var str = '';
            if (product.barcode) {
                str += '|' + product.barcode;
            }
            if (product.default_code) {
                str += '|' + product.default_code;
            }
            var packagings = this.packagings_by_product_tmpl_id[product.product_tmpl_id] || [];
            for (var i = 0; i < packagings.length; i++) {
                str += '|' + packagings[i].barcode;
            }
            str  = product.id + ':' + str.replace(/:/g,'') + '\n';
            return str;
        },
    });
});
