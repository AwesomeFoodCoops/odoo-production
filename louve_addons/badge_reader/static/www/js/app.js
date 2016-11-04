// Ionic Starter App

// angular.module is a global place for creating, registering and retrieving Angular modules
// 'starter' is the name of this angular module example (also set in a <body> attribute in index.html)
// the 2nd parameter is an array of 'requires'
angular.module('starter', ['ionic', 'ui.router', 'odoo'])

.run(function($ionicPlatform) {
    $ionicPlatform.ready(function() {
        // Hide the accessory bar by default (remove this to show the 
        //accessory bar above the keyboard for form inputs)
        if(window.StatusBar) {
            StatusBar.styleDefault();
        }
    });
})
.run(['jsonRpc', '$state', '$rootScope', function (jsonRpc, $state, $rootScope) {
    jsonRpc.errorInterceptors.push(function (a) {
        if (a.title === 'session_expired')
            $state.go('login');
    });
    $rootScope.logout = function() {
        $state.go('logout');
    };
}])
.config(['$stateProvider','$urlRouterProvider' , function ($stateProvider, $urlRouterProvider) {
  $stateProvider.state(
    'login', {
        url: '/login',
        templateUrl: 'views/v_login.html',
        controller: 'LoginCtrl'
  }).state(
    'logout', {
        url: '/logout',
        templateUrl: 'views/v_login.html',
        controller: 'LoginCtrl'
  }).state(
    'partner_search', {
        url: '/partner_search',
        templateUrl: 'views/v_partner_search.html',
        controller: 'PartnerSearchCtrl'
  }).state(
    'partner_form', {
        url: '/partner_form/:partner_id',
        templateUrl: 'views/v_partner_form.html',
        controller: 'PartnerFormCtrl'
  });
  $urlRouterProvider.otherwise('login');
}]);
