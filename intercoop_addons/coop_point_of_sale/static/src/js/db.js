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
        },
        // allow searching by barcode_base
        _partner_search_string: function(partner){
            var str =  partner.name;
            var split_str = '___';

            if(partner.barcode){
                str += split_str + partner.barcode;
            }
            if(partner.barcode_base){
                str += split_str + partner.barcode_base;
            }
            if(partner.phone){
                str += split_str + partner.phone.split(' ').join('');
            }
            if(partner.mobile){
                str += split_str + partner.mobile.split(' ').join('');
            }
            if(partner.email){
                str += split_str + partner.email;
            }
            str = '' + partner.id + ':' + str.replace(':','') + split_str + '\n';
            return str;
        },
        // apply the equal search
        search_partner: function(query){
            var split_str = '___';
            try {
                query = query.replace(/[\[\]\(\)\+\*\?\.\-\!\&\^\$\|\~\_\{\}\:\,\\\/]/g,'.');
                query = query.replace(/ /g,'.+');
                if (!isNaN(query)){
                    query = split_str + query + split_str;
                }
                var re = RegExp("([0-9]+):.*?"+query,"gi");

            }catch(e){
                return [];
            }
            var results = [];
            for(var i = 0; i < this.limit; i++){
                var r = re.exec(this.partner_search_string);
                if(r){
                    var id = Number(r[1]);
                    results.push(this.get_partner_by_id(id));
                }else{
                    break;
                }
            }
            return results;
        },
    });

});
