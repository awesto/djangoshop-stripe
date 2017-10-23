(function() {
"use strict";

var module = angular.module('django.shop.stripe', ['angular-stripe']);

// Directive <ANY stripe-card-form>
// Must be added to the form containing the CC input fields
module.directive('stripeCardForm', ['$http', '$log', '$q', 'stripe', function($http, $log, $q, stripe) {
	// iterate over sibling scopes to find the scope object holding the customer's data
	function findCustomerScope(scope) {
		while (scope) {
			if (scope.hasOwnProperty('customer'))
				return scope.customer;
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
						customer.last_name ? customer.last_name : ''
					].join(' ')}
				};
			}

			$scope.prepare = function() {
				$scope.dismiss();
				return function(response) {
					var deferred;
					if ($scope.payment_method.payment_modifier !== 'stripe-payment'
					  || angular.isObject($scope.payment_method.payment_data))
						return $q.resolve(response);

					// pass data from Stripe Card Form to PSP and fetch the token
					deferred = $q.defer();
					stripe.card.createToken($scope.payment.card).then(function(token) {
						$log.log("Token created for card ending in ", token.card.last4);
						$scope.payment_method.payment_data = {token_id: token.id};
						$scope.payment.card = {name: $scope.payment.card.name};  // forget credit card number immediately
						deferred.resolve(response);
					}).catch(function(error) {
						$log.error(error.message);
						$scope.stripe_error_message = error.message;
						deferred.reject(response);
					});
					return deferred.promise;
				}
			};

			$scope.resetStripeToken = function() {
				$scope.payment_method.payment_data = null;
				$scope.dismiss();
			};

			$scope.dismiss = function() {
				$scope.stripe_error_message = $scope.stripe_success_message = null;
			};

			$scope.resetStripeToken();
		}],
		link: function(scope, element) {
			if (!angular.isObject(scope.payment_method))
				throw new Error("Local scope can not manage the Payment Method Form. Did you forget to wrap it into a 'Set of Forms' plugin?");
		}
	};
}]);

})();
