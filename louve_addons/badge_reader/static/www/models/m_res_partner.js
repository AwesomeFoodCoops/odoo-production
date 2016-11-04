'use strict';


angular.module('starter').factory('ResPartnerModel', ['$q', 'jsonRpc', function ($q, jsonRpc) {

    return {
        GetByBarcode: function(barcode) {
            return jsonRpc.searchRead('res.partner', [['barcode', '=', barcode]], ['id']).then(function (partner_res) {
                return partner_res.records;
            });
        },

        LogMove: function(partner_id) {
            return jsonRpc.call('res.partner', 'log_move', [partner_id]).then(function (res) {
                return res;
            });
        },

        GetById: function(partner_id) {
            return jsonRpc.searchRead('res.partner', [['id', '=', partner_id]], [
                'id', 'name', 'street', 'street2', 'zip', 'city', 'customer', 'country_id', 'phone', 'mobile', 'bootstrap_cooperative_state', 'cooperative_state']).then(function (partner_res) {
                if (partner_res.records.length == 1){
                    var res = partner_res.records[0];
                    res.image_url = "../../../web/image?model=res.partner&id=" + partner_id + "&field=image";
                    return res;
                }else{
                    return false;
                }
            });
        },
    };
}]);
