(function() {
"use strict";

var module = angular.module('django.shop.stripe', ['djng.urls', 'angular-stripe']);

// Directive <ANY stripe-card-form>
// Must be added to the form containing the CC input fields
module.directive('stripeCardForm', ['$http', 'djangoUrl', 'stripe',
                           function($http, djangoUrl, stripe) {
	// iterate over sibling scopes to find the scope object holding the customer's data
	function findCustomerScope(scope) {
		while (scope && scope.hasOwnProperty('data')) {
			if (scope.data.hasOwnProperty('customer'))
				return scope.data.customer;
			scope = scope.$$prevSibling;
		}
		return null;
	}

	return {
		restrict: 'A',
		require: 'form',
		scope: false,
		controller: ['$scope', function($scope) {
			var customer = findCustomerScope($scope);
			if (customer) {
				$scope.payment = {
					card: {name: [
					    customer.first_name ? customer.first_name : '',
					    customer.last_name ? customer.last_name : ''].join(' ')
					}
				};
			}
			if (!angular.isObject($scope.data.payment_method)) {
				$scope.data.payment_method = {};
			}

			// pass data from Stripe Card Form to PSP and fetch the token
			function createToken(deferred) {
				$scope.dismiss();
				stripe.card.createToken($scope.payment.card).then(function(token) {
					console.log('token created for card ending in ', token.card.last4);
					deferred.resolve(token);
				}, function(error) {
					console.log(error.message);
					$scope.stripe_error_message = error.message;
					deferred.reject(error.code);
				});
				return deferred.promise;
			}

			$scope.prepare = function(deferred) {
				if ($scope.data.payment_method.payment_modifier !== 'stripe-payment'
				  || angular.isString($scope.data.payment_method.payment_data.token_id)) {
					deferred.resolve();
				} else {
					createToken(deferred).then(function(token) {
						$scope.data.payment_method.payment_data = {token_id: token.id};
					});
				}
				return deferred.promise;
			};

			$scope.resetStripeToken = function() {
				$scope.data.payment_method.payment_data = {};
				$scope.dismiss();
			};

			$scope.dismiss = function() {
				$scope.stripe_error_message = $scope.stripe_success_message = null;
			};

			$scope.resetStripeToken();
		}]
	};
}]);

})();
