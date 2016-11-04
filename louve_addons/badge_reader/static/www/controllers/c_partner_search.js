'use strict';


angular.module('starter').controller('PartnerSearchCtrl', ['$scope', '$state', 'ResPartnerModel', '$document', function ($scope, $state, ResPartnerModel, $document) {


    $scope.search_value = {
        'css_class': 'partner-search',
    };

    $scope.submit_barcode = function () {
        ResPartnerModel.GetByBarcode($scope.search_value.barcode).then(function (partner_res) {
            if (partner_res.length == 1){
                $scope.search_value.css_class = 'partner-search';
                $scope.errorMessage = '';
                ResPartnerModel.LogMove(partner_res[0].id).then(function (res) {
                    $state.go('partner_form', {partner_id: partner_res[0].id});
                });
            }
            else{
                $scope.search_value.css_class = 'partner-danger';
                $scope.errorMessage = 'Membre non trouvé';
                $document[0].getElementById('sound_res_partner_not_found').play();
            }
        });
    };
}]);
