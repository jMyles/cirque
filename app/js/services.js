'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('cirque.services', [])
  .factory('User', function($resource) {
    return $resource('/api/users/:id/');
  })
  .factory('CJDNSRoute', function($resource) {
    return $resource('/api/cjdnsroutes/:id/');
  });
