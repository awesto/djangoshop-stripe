(function() {
"use strict";

var shopStripe = angular.module('django.shop.stripe', ['ng.django.urls', 'angular-stripe']);

shopStripe.directive('stripeCardForm', ['$http', 'djangoUrl', 'stripe', function($http, djangoUrl, stripe) {
	var chargeCreditcardURL = djangoUrl.reverse('shop:stripe-payment:charge');

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
				$scope.payment = {card: {name: [
				    customer.first_name ? customer.first_name : '',
				    customer.last_name ? customer.last_name : ''].join(' ')
				}};
			}

			$scope.charge = function() {
				$scope.dismiss();
				// pass gathered data to Stripe and fetch the token
				var promise = stripe.card.createToken($scope.payment.card);
				return promise.then(function(token) {
					var payment = angular.copy($scope.payment);
					console.log('token created for card ending in ', token.card.last4);
					payment.card = void 0;
					payment.token = token.id;
					return $http.post(chargeCreditcardURL, payment);
				}, function(error) {
					console.error(error.code);
					$scope.stripe_error_message = error.message;
					return promise;
				});
			};

			$scope.dismiss = function() {
				$scope.stripe_error_message = $scope.stripe_success_message = null;
			};
		}]
	};
}]);

})();
