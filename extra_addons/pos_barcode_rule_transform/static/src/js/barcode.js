///*
//    Copyright (C) 2019-Today: Druidoo (https://www.druidoo.io)
//    @author: Iván Todorovich <ivan.todorovich@druidoo.io>
//    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
//*/

odoo.define('pos_barcode_rule_transform.BarcodeParser', function (require) {
    "use strict";

    var BarcodeParser = require('barcodes.BarcodeParser');
    var Model = require('web.Model');

    /*
    Include some hooks. Nothing more
    Could be moved to a standalone module
    */
    BarcodeParser.include({

        _barcode_rule_query_fields: function() {
            return ['name', 'sequence', 'type', 'encoding', 'pattern', 'alias'];
        },

        /*
        Overload to add hooks:
            _barcode_rule_query_fields
        */
        load: function(){
            var self = this;
            return new Model('barcode.nomenclature')
                .query(['name','rule_ids','upc_ean_conv'])
                .filter([['id','=',this.nomenclature_id[0]]])
                .first()
                .then(function(nomenclature){
                    self.nomenclature = nomenclature;
                    return new Model('barcode.rule')
                        //.query(['name','sequence','type','encoding','pattern','alias'])
                        .query(self._barcode_rule_query_fields())
                        .filter([['barcode_nomenclature_id','=',self.nomenclature.id ]])
                        .all();
                }).then(function(rules){
                    rules = rules.sort(function(a,b){ return a.sequence - b.sequence; });
                    self.nomenclature.rules = rules;
                });
        },


        /*
        Overload to add hooks:
            _apply_rule_parsed_result
        */
        parse_barcode: function(barcode){
            var parsed_result = {
                encoding: '',
                type:'error',  
                code:barcode,
                base_code: barcode,
                value: 0,
            };

            if (!this.nomenclature) {
                return parsed_result;
            }

            var rules = this.nomenclature.rules;
            for (var i = 0; i < rules.length; i++) {
                var rule = rules[i];
                var res = this.try_rule(parsed_result, barcode, rule);
                if (res) { return res; }
            }
            return parsed_result;
        },

        try_rule: function(parsed_result, barcode, rule) {
            var cur_barcode = barcode;
            if (    rule.encoding === 'ean13' && 
                    this.check_encoding(barcode,'upca') &&
                    this.nomenclature.upc_ean_conv in {'upc2ean':'','always':''} ){
                cur_barcode = '0' + cur_barcode;
            } else if (rule.encoding === 'upca' &&
                    this.check_encoding(barcode,'ean13') &&
                    barcode[0] === '0' &&
                    this.upc_ean_conv in {'ean2upc':'','always':''} ){
                cur_barcode = cur_barcode.substr(1,12);
            }

            if (!this.check_encoding(cur_barcode,rule.encoding)) {
                return false;
            }

            var match = this.match_pattern(cur_barcode, rule.pattern, rule.encoding);
            if (match.match) {
                if(rule.type === 'alias') {
                    barcode = rule.alias;
                    parsed_result.code = barcode;
                    parsed_result.type = 'alias';
                } else {
                    parsed_result.encoding  = rule.encoding;
                    parsed_result.type      = rule.type;
                    parsed_result.value     = match.value;
                    parsed_result.code      = cur_barcode;
                    if (rule.encoding === "ean13"){
                        parsed_result.base_code = this.sanitize_ean(match.base_code);
                    } else {
                        parsed_result.base_code = match.base_code;
                    }
                    return parsed_result;
                }
            }
        },

    });


    /*
    Actual implementation of barcode transform
    */
    BarcodeParser.include({
        _barcode_rule_query_fields: function() {
            var res = this._super.apply(this, arguments);
            res.push('transform_expr');
            return res;
        },

        try_rule: function(parsed_result, barcode, rule) {
            var res = this._super.apply(this, arguments);
            if (res && res.value && rule.transform_expr) {
                try {
                    res.original_value = res.value;
                    var new_value = py.eval(rule.transform_expr, {
                        value: res.value,
                        code: res.code,
                        barcode: res.code,
                    });
                    if (typeof new_value !== "number") {
                        throw new TypeError('Transformed value should be a Number. Got this instead: ' + new_value + ' (' + typeof new_value + ')')
                    }
                    res.value = new_value;
                } catch(err) {
                    console.error('Unable to apply transform expression:', rule.transform_expr, err)
                }
            }
            return res;
        },
    });

    return BarcodeParser;
    
});
