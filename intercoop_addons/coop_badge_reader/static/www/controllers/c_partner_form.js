'use strict';


angular.module('starter').controller('PartnerFormCtrl', ['$scope', '$state', 'ResPartnerModel', '$document', function ($scope, $state, ResPartnerModel, $document) {

    $scope.partner = {};

    $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
        if (toState.name == 'partner_form'){
            // Adding extensions for partner if current user is suspended (logic defined in Backend)
            ResPartnerModel.GracePartner(parseInt(toParams['partner_id'])).then(function (grace_result){
                ResPartnerModel.GetById(toParams['partner_id']).then(function (partner_res){
                    partner_res.css_class = 'partner-' + partner_res.bootstrap_cooperative_state;
                    $document[0].getElementById('sound_res_partner_' + partner_res.bootstrap_cooperative_state).play();
                    $scope.partner = partner_res;
                });
            });
        }
    });

    $scope.partner_in = function () {
        ResPartnerModel.LogMove($scope.partner.id, 'in').then(function (res) {
            $state.go('partner_search');
        });
    };

    $scope.partner_out = function () {
        ResPartnerModel.LogMove($scope.partner.id, 'out').then(function (res) {
            $state.go('partner_search');
        });
    };

    $scope.partner_wrong = function () {
        ResPartnerModel.LogMove($scope.partner.id, 'wrong').then(function (res) {
            $state.go('partner_search');
        });
    };

    $scope.set_badge_distributed = function(){        
        ResPartnerModel.SetBadgeDistributed($scope.partner.id).then(function(res){
           $state.reload();
        })
    }

}]);
