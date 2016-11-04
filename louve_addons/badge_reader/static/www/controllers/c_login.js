'use strict';


angular.module('starter').controller('LoginCtrl', ['$scope', 'jsonRpc', '$state', function ($scope, jsonRpc, $state) {

    $scope.login = {};

    $scope.submit = function () {
        jsonRpc.login($scope.login.db, $scope.login.username, $scope.login.password).then(function (user) {
            jsonRpc.call('res.users', 'check_group', ['badge_reader.group_manager']).then(function (res) {
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
