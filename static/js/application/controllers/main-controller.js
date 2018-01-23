ngApp.controller('MainCtrl', ['$scope',  
	function($scope) {
		
		$scope.message = "it works!";
		/*$scope.newTodo = {};
		
		var todosResource = Restangular.all('api/v1/todos');
		
		loadTodoList();
		
		function loadTodoList() {
			todosResource.getList().then(function(data) {
				console.log("data:", data);
				$scope.todos = data.objects;
				console.log("$scope.todos:", $scope.todos);
			});
		}
		
		
		$scope.saveTodo = function() {
			$scope.todos.post($scope.newTodo);
			loadTodoList();
		}

		
		$scope.deleteTodo = function(todo) {
			todo.remove().then(function(data) {
				loadTodoList();
			});
		}*/
    }
]);
