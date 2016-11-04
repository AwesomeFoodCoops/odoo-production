'use strict';


angular.module('starter').controller('PartnerFormCtrl', ['$scope', '$state', 'ResPartnerModel', '$document', function ($scope, $state, ResPartnerModel, $document) {

    $scope.partner = {};

    $scope.go_back = function () {
        $state.go('partner_search');
    };

    $scope.$on('$stateChangeSuccess', function(event, toState, toParams, fromState, fromParams){
        // TODO Add test or ask to hpar how to fire this event, only when needed
        if (toState.name == 'partner_form'){
            ResPartnerModel.GetById(toParams['partner_id']).then(function (partner_res) {
                // Add style and Sound
                partner_res.css_class = 'partner-' + partner_res.bootstrap_cooperative_state;
                $document[0].getElementById('sound_res_partner_' + partner_res.bootstrap_cooperative_state).play();
                $scope.partner = partner_res;
            });
        }
    });
}]);
