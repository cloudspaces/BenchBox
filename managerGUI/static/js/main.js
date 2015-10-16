var app = angular.module('app', ['ngRoute']);

// angular js directives
app.directive('hello', [function () {
    return {
        restrict: 'CEA', // C: class, E: element, M: comments, A: attributes
        replace: true, // replaces original content with template
        template: '<span><br>Hello</span>'
    }
}]);


// angular js controllers
app.controller('TodoController', ['$scope', function ($scope) {
    $scope.todos = [
        {name: 'Master HTML/CSS/Javascript', completed: true},
        {name: 'Learn AngularJS', completed: false},
        {name: 'Build NodeJS backend', completed: false},
        {name: 'Get started with ExpressJS', completed: false},
        {name: 'Setup MongoDB database', completed: false},
        {name: 'Be awesome!', completed: false},
    ]
}]);

// angular js routes (ngRoutes)
app.config(['$routeProvider', function ($routeProvider) {
    $routeProvider
        .when('/', {
            templateUrl: '/todos.html',
            controller: 'TodoController'
        });
}]);


// factory
app.factory('Todos', function(){
        return [
            { name: 'AngularJS Directives', completed: true, note: 'add notes...' },
            { name: 'Data binding', completed: true, note: 'add notes...' },
            { name: '$scope', completed: true, note: 'add notes...' },
            { name: 'Controllers and Modules', completed: true, note: 'add notes...' },
            { name: 'Templates and routes', completed: true, note: 'add notes...' },
            { name: 'Filters and Services', completed: false, note: 'add notes...' },
            { name: 'Get started with Node/ExpressJS', completed: false, note: 'add notes...' },
            { name: 'Setup MongoDB database', completed: false, note: 'add notes...' },
            { name: 'Be awesome!', completed: false, note: 'add notes...' },
        ];
    })

    .controller('TodoController', ['$scope', 'Todos', function ($scope, Todos) {
        $scope.todos = Todos;
    }])

    .controller('TodoDetailCtrl', ['$scope', '$routeParams', 'Todos', function ($scope, $routeParams, Todos) {
        $scope.todo = Todos[$routeParams.id];
    }])

    .config(['$routeProvider', function ($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: '/todos.html',
                controller: 'TodoController'
            })

            .when('/:id', {
                templateUrl: '/todoDetails.html',
                controller: 'TodoDetailCtrl'
            });
    }]);


app.controller('AddHostCtrl', ['$scope', function($scope){
    $scope.rows = ['Row 1', 'Row 2'];

    $scope.counter = 3;

    $scope.addRow = function() {

        $scope.rows.push('Row ' + $scope.counter);
        $scope.counter++;
    }
}])



