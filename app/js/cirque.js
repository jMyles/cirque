angular.module('cirque', [
  'cirque.services',
  'ngResource',
])
  .config(function ($interpolateProvider, $httpProvider, $resourceProvider) {
// Force angular to use square brackets for template tag
// The alternative is using {% verbatim %}
$interpolateProvider.startSymbol('[[').endSymbol(']]');
// CSRF Support
$httpProvider.defaults.xsrfCookieName = 'csrftoken';
$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
// This only works in angular 3!
// It makes dealing with Django slashes at the end of everything easier.
// $resourceProvider.defaults.stripTrailingSlashes = false;
})
  .controller('UserCtrl', function UserCtrl($scope, User) {
  $scope.users = {};

  User.query(function(response){
    $scope.users = response;
  });
})
  .controller('CJDNSRouteCtrl', function CJDNSRouteCtrl($scope, CJDNSRoute) {
    $scope.cjdnsRoutes = {};
    
    CJDNSRoute.query(function(response){
        $scope.cjdnsRoutes = response;
  });
});
