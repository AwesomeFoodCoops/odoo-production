odoo.define('pos_search_improvement.models.init', function(require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields('product.product', ['multi_barcode_ids']);
    
    models.load_models([
        {
            model:  'product.multi.barcode',
            fields: ['barcode', 'product_id'],
            domain: [],
            loaded: function(self, barcodes){
                self.db.set_multi_barcodes(barcodes)
            },
        },
    ],{'before': 'product.product'});

})
