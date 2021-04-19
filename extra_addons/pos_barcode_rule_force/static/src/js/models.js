///*
//    Copyright (C) 2019-Today: Druidoo (https://www.druidoo.io)
//    @author: Iván Todorovich <ivan.todorovich@druidoo.io>
//    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
//*/

odoo.define('pos_barcode_rule_force.models', function (require) {
    "use strict";

    // we require pos_barcode_rule_transform.BarcodeParser
    // instead of barcodes.BarcodeParser because of the hooks
    var BarcodeParser = require('pos_barcode_rule_transform.BarcodeParser');
    var models = require('point_of_sale.models');
    
    // Load field on pos init
    models.load_fields('product.product', ['force_barcode_rule_id']);

    var _super_PosModel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        scan_product: function (parsed_code) {
            var barcode = parsed_code.base_code;
            var product = this.db.get_product_by_barcode(parsed_code.base_code);
            if (product && product.force_barcode_rule_id) {
                var rule_ids = this.barcode_reader.barcode_parser.nomenclature.rule_ids;
                var rules = this.barcode_reader.barcode_parser.nomenclature.rules;
                var i = rule_ids.indexOf(product.force_barcode_rule_id[0]);
                if (i === -1) {
                    return console.error('Unable to force barcode rule, rule', product.force_barcode_rule_id, 'is not present in the BarcodeParser.')
                }
                var rule = rules[i];
                parsed_code = this.barcode_reader.barcode_parser.try_rule(parsed_code, parsed_code.code, rule);
                if (!parsed_code){
                    // S#25874: there is an error when the barcode doesn't match the rule
                    parsed_code = {
                        encoding: '',
                        type:'error',  
                        code: barcode,
                        base_code: barcode,
                        value: 0,
                    };
                }
                return _super_PosModel.scan_product.apply(this, [parsed_code]);
            }
            // normal behaviour
            return _super_PosModel.scan_product.apply(this, arguments);
        },
    });

});
