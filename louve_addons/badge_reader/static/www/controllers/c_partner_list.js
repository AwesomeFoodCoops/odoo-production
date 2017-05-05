'use strict';


angular.module('starter').controller('PartnerListCtrl', ['$scope', '$state', 'ResPartnerModel', '$document', function ($scope, $state, ResPartnerModel, $document) {

    $scope.partners = [];

    $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
        if (toState.name == 'partner_list'){
            var partner_ids = toParams['partner_ids'].split(',');
            ResPartnerModel.GetByIds(partner_ids).then(function (partner_res) {
                $scope.partners = partner_res;
            });
        }
    });

    $scope.selectPartner = function (partner_id) {
        $state.go('partner_form', {partner_id: partner_id});
    };

}]);
