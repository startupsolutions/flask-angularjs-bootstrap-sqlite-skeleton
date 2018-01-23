// ----------------------------------------------------------------------------

var ngApp = angular.module('ngApp', ['ngRoute']);


console.log("$ORIGIN:", $ORIGIN);

ngApp.apiBaseUrl = $ORIGIN.apiBaseUrl;


// ngRoute config
ngApp.config(function($routeProvider) {
    $routeProvider
        .when('/',        { templateUrl: 'static/views/home.html' })
        .when('/about',   { templateUrl: 'static/views/about.html' })
        .when('/contact', { templateUrl: 'static/views/contact.html' })
});


