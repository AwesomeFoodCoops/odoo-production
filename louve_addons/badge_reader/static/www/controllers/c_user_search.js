'use strict';


angular.module('starter').controller('UserSearchCtrl', ['$scope', '$state', 'ResUsersModel', '$document', function ($scope, $state, ResUsersModel, $document) {


    $scope.search_value = {
        'css_class': 'partner-search',
    };

    $scope.submit_barcode = function () {
        ResUsersModel.GetByBarcode($scope.search_value.barcode).then(function (user_res) {
            if (user_res.length == 1){
                $scope.search_value.css_class = 'partner-search';
                $scope.errorMessage = '';
                ResUsersModel.LogMove(user_res[0]['id']).then(function (res) {
                    $state.go('partner_form', {partner_id: user_res[0]['partner_id'][0]});
                });
            }
            else{
                $scope.search_value.css_class = 'partner-danger';
                $scope.errorMessage = 'Membre non trouvé';
                $document[0].getElementById('sound_res_users_not_found').play();
            }
        });
    };
}]);
