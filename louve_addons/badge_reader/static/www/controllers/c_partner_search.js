'use strict';


angular.module('starter').controller('PartnerSearchCtrl', ['$scope', '$state', 'ResPartnerModel', '$document', function ($scope, $state, ResPartnerModel, $document) {


    $scope.search_value = {
        'css_class': 'partner-search',
        'barcode': '',
        'barcode_base': '',
        'partner_name': '',
    };

    $scope.$on(
            '$stateChangeSuccess',
            function(event, toState, toParams, fromState, fromParams){
        if ($state.current.name === 'partner_search') {
            // Init Barcode value
            document.querySelector('#barcode').focus();
            $scope.search_value.barcode = '';
            $scope.search_value.barcode_base = '';
            $scope.search_value.partner_name = '';
            $scope.search_value.css_class = 'partner-search';
            $scope.errorMessage = '';
        }
    });

    function manage_result(search_type, partner_ids) {
        if (partner_ids.length == 0){
            manage_not_found(search_type);
        }
        else if (partner_ids.length == 1){
            manage_one_match(partner_ids[0]);
        }
        else{
            manage_many_matches(partner_ids);
        }
    };

    function manage_not_found(search_type) {
        if (search_type == 'barcode'){
            $scope.search_value.css_class = 'partner-danger';
            $scope.errorMessage = 'Code Barre incorrect';
            $document[0].getElementById('sound_res_partner_not_found').play();
        }

        if (search_type == 'barcode_base'){
            $scope.search_value.css_class = 'partner-danger';
            $scope.errorMessage = 'Numéro de membre incorrect';
            $document[0].getElementById('sound_res_partner_not_found').play();
        }

        if (search_type == 'partner_name'){
            $scope.search_value.css_class = 'partner-danger';
            $scope.errorMessage = 'Recherche par nom ou prénom infructueuse';
            $document[0].getElementById('sound_res_partner_not_found').play();
        }
    };

    function manage_one_match(partner_id) {
        $state.go('partner_form', {partner_id: partner_id});
    };

    function manage_many_matches(partner_ids) {
        $state.go('partner_list', {partner_ids: partner_ids});
    };

    $scope.search_partner = function () {
        // Search by Barcode
        if ($scope.search_value.barcode != ''){
            ResPartnerModel.GetByBarcode($scope.search_value.barcode).then(function (partner_ids) {
                manage_result('barcode', partner_ids);
            });
        }

        else {
            // Search by Barcode Base
            if ($scope.search_value.barcode_base != ''){
                ResPartnerModel.GetByBarcodeBase($scope.search_value.barcode_base).then(function (partner_ids) {
                    manage_result('barcode_base', partner_ids);
                });
            }
            else {
                // Search by Name
                if ($scope.search_value.partner_name != ''){
                    ResPartnerModel.GetByName($scope.search_value.partner_name).then(function (partner_ids) {
                        manage_result('partner_name', partner_ids);
                    });
                }
                else{
                    $scope.search_value.css_class = 'partner-danger';
                    $scope.errorMessage = 'Champs de recherche requis';
                }
            }
        }
    };
}]);
