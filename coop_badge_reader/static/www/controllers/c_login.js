'use strict';

angular.module('starter').controller('LoginCtrl', ['$scope', 'jsonRpc', '$state', '$stateParams', function ($scope, jsonRpc, $state, $stateParams) {

    $scope.login = {};

    $scope.init = function () {
        // Set focus
        angular.element(document.querySelector('#database'))[0].focus();
        // prefill form with GET parameters
        $scope.login.db = $stateParams['db'];
        $scope.login.username = $stateParams['username'];
        $scope.login.password = $stateParams['password'];

        // Auto Submit if all params are provided
        if ($stateParams['db'] != undefined &&
                $stateParams['username'] != undefined &&
                $stateParams['password'] != undefined){
            $scope.submit();
        }
    };

    $scope.submit = function () {
        jsonRpc.login($scope.login.db, $scope.login.username, $scope.login.password).then(function (user) {
            jsonRpc.call('res.users', 'user_has_groups', [user.id, 'coop_badge_reader.group_time_clock']).then(function (res) {
                if (res){
                    $scope.login.css_class = 'authentication-ok';
                    $scope.errorMessage = "";
                    $state.go('partner_search');
                }
                else{
                    $scope.login.css_class = 'authentication-acces-right-problem';
                    $scope.errorMessage = "Droits d'accès incorrects";
                }
            });

        }, function(e) {
            $scope.login.css_class = 'authentication-incorrect';
            $scope.errorMessage = "Identifiants incorrects";
        });
    };
}]);
