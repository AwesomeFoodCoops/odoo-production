odoo.define('pos_search_improvement.db', function (require) {
    "use strict";

    var PosDB = require('point_of_sale.DB');
    var _super = PosDB.prototype;

    PosDB.include({

        init: function(options){
            this._super(options);
            this.multi_barcode_by_id = {};
        },

        // Overide _product_search_string to allow searching product by
        // Internal Reference and Barcode Only
        _product_search_string: function(product){
            var str = '';
            if (product.barcode) {
                str += '|' + product.barcode;
            }
            // Set Multi barcode for product
            var multi_barcode_ids = product.multi_barcode_ids;
            if (multi_barcode_ids) {
                var multi_barcodes = this.get_multi_barcodes()
                for (var index in multi_barcode_ids) {
                    var barcode_id = multi_barcode_ids[index];
                    var multi_barcode = multi_barcodes[barcode_id];
                    str += '|' + multi_barcode.barcode;
                }
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
        add_products: function(products){
            var res = this._super(products);
            var multi_barcodes = this.get_multi_barcodes();
            this.add_multi_barcode_for_product(multi_barcodes);
        },
        add_multi_barcode_for_product: function(barcodes){
            for (var i in barcodes){
                var line = barcodes[i];
                if(line.barcode){
                    var product = line.product_id;
                    product = this.product_by_id[product[0]];
                    if(product){
                        this.product_by_barcode[line.barcode] = product;
                    }
                }
            }
        },
        set_multi_barcodes: function(barcodes){
            for (var i=0; i<barcodes.length; i++){
                var barcode = barcodes[i];
                this.multi_barcode_by_id[barcode.id] = barcode;
            }
        },
        get_multi_barcodes: function(){
            return this.multi_barcode_by_id;
        },

        search_product_in_category: function(category_id, query){

            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
            }catch(e){
                return [];
            }
            var res = this._super(category_id, query);
            var results = [];

            for(var i = 0; i < res.length; i++){
                var multi_barcodes = this.get_multi_barcodes()
                var barcode_ids = res[i].multi_barcode_ids;
                if(res[i].barcode === query || res[i].default_code === query || res[i].description_sale === query || res[i].description === query){
                    results.push(res[i]);
                }else if (barcode_ids){
                    for (var j = 0; j < barcode_ids.length; j ++){
                        if (multi_barcodes[barcode_ids[j]].barcode === query){ 
                            results.push(res[i]);
                        }
                    }
                } else{
                    break;
                }
            }
            return results;
        },

    });
});
