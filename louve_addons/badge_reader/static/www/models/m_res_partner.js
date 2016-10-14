'use strict';


angular.module('starter').factory('ResPartnerModel', ['$q', 'jsonRpc', function ($q, jsonRpc) {

    return {
        GetById: function(partner_id) {
            return jsonRpc.searchRead('res.partner', [['id', '=', partner_id]], [
                'id', 'name', 'street', 'street2', 'zip', 'city', 'customer', 'country_id', 'phone', 'mobile', 'bootstrap_state', 'state']).then(function (partner_res) {
                if (partner_res.records.length == 1){
                    var res = partner_res.records[0];
                    res.image_url = "../../../web/image?model=res.partner&id=" + partner_id + "&field=image";
                    return res;
                }else{
                    return false;
                }
            });
        }
    };
}]);
