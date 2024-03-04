'use strict';


angular.module('starter').controller('PartnerFormCtrl', ['$scope', '$state',  '$sce', 'ResPartnerModel', '$document', function ($scope, $state, $sce, ResPartnerModel, $document) {

    $scope.partner = {};

    $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
        if (toState.name == 'partner_form'){
            // Adding extensions for partner if current user is suspended (logic defined in Backend)
            ResPartnerModel.GracePartner(parseInt(toParams['partner_id'])).then(function (grace_result){
                ResPartnerModel.GetById(toParams['partner_id']).then(function (partner_res){
                    partner_res.css_class = 'partner-' + partner_res.bootstrap_cooperative_state;
                    if (partner_res.error_message) {
                        partner_res.css_class = 'partner-error';
                    }
                    $document[0].getElementById('sound_res_partner_' + partner_res.bootstrap_cooperative_state).play();
                    $scope.partner = partner_res;
                    $scope.contact_us_message = $sce.trustAsHtml(partner_res.contact_us_message);
                    if (partner_res.cooperative_state == 'delay' && grace_result) {
                        var date_stop_str = grace_result.slice(8, 10) + '/' + grace_result.slice(5, 7) + '/' + grace_result.slice(0, 4);
                        $scope.warning_message = $sce.trustAsHtml("Un délai de grâce jusqu'a " + date_stop_str + " ou jusqu'à votre prochain service vous a été attribué. Vous pouvez faire vos courses !");
                    } else if (partner_res.cooperative_state == 'suspended') {
                        console.log(partner_res)
                        $scope.fail_message = $sce.trustAsHtml("Nous n'avons pas pu vous attribuer de délai de grâce, vous devez rattraper vos services avant de faire vos courses.")
                    }
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
