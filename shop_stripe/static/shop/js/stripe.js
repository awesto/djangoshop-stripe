(function() {
"use strict";

var module = angular.module('django.shop.stripe', ['angular-stripe']);

// Directive <form stripe-card-form ...>
// Must be added to the form containing the CC input fields
module.directive('stripeCardForm', ['$http', '$log', '$q', '$timeout', 'stripe', function($http, $log, $q, $timeout, stripe) {
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

			$scope.payment_method.payment_data = null;
		}],
		link: {
			pre: function(scope) {
				scope.prepare = function() {
					return function(response) {
						var deferred, response;

						if (scope.payment_method.payment_modifier !== 'stripe-payment'
						  || angular.isObject(scope.payment_method.payment_data))
							return $q.resolve();

						// pass data from Stripe Card Form to PSP and fetch the token
						deferred = $q.defer();
						stripe.card.createToken(scope.payment.card).then(function(token) {
							$log.log("Token created for card ending in ", token.card.last4);
							scope.payment_method.payment_data = {token_id: token.id};
							$timeout(function() {
								// forget credit card number after 3 seconds
								scope.payment.card = {name: scope.payment.card.name};
								scope.stripe_card_form.$setSubmitted();
							}, 3000);

							// emulate a response object for the next promise handler, since `stripe.card.createToken()`
							// returns a proprietary and incompatible token object
							response = {
								status: 200,
								statusText: "OK",
								data: {}
							};
							deferred.resolve(response);
						}).catch(function(error) {
							var fieldName = error.param;
							$log.log(error.type + ": " + error.message);
							if (error.type === 'card_error') {
								scope.stripe_card_form[fieldName].$message = error.message;
								scope.stripe_card_form[fieldName].$setValidity('rejected', false);
								scope.stripe_card_form[fieldName].$setPristine();
							}
							scope.stripe_card_form.$setSubmitted();

							// emulate a response object for the next promise handler, since `stripe.card.createToken()`
							// returns a proprietary and incompatible error object
							response = {
								status: 422,
								statusText: error.code,
								data: {stripe_card_form: {}}
							};
							response.data.stripe_card_form[fieldName] = {};
							deferred.reject(response);
						});
						return deferred.promise;
					};
				};
			},
			post: function(scope, element, attrs, formController) {
				var watcher;
				if (!angular.isObject(scope.payment_method))
					throw new Error("Local scope can not manage the Payment Method Form. Did you forget to wrap it into a 'Set of Forms' plugin?");

				watcher = scope.$watch('payment_method.payment_modifier', function (value) {
					if (value !== 'stripe-payment') {
						formController._previous_$valid = formController.$valid;
						// enforce the Stripe form to be valid, so that the wrapping formsSet is valid
						formController.$valid = true;
						formController.$invalid = false;
					} else if (formController.hasOwnProperty('_previous_$valid')) {
						// restore the previous valid state of the form
						formController.$valid = formController._previous_$valid;
						formController.$invalid = !formController.$valid;
						delete formController._previous_$valid;
					}
				});
				scope.$on('$destroy', watcher);
			}
		}
	};
}]);


angular.forEach(['input', 'select'], function(element) {
	module.directive(element, ['$timeout', function($timeout) {
		return {
			require: ['^?stripeCardForm', '^?form', '?ngModel'],
			restrict: 'E',
			priority: 2,
			link: function(scope, element, attrs, controllers) {
				var formController = controllers[1], modelController = controllers[1];
				if (!controllers[0] || !formController || !modelController)
					return;  // outside <form stripe-card-form ...>

				$timeout(function() {
					formController[attrs.name].$setPristine();
				});

				element.on('change', function(event) {
					if (formController[attrs.name].$error.rejected) {
						formController[attrs.name].$setValidity('rejected', true);
						formController[attrs.name].$submitted = false;
						scope.$apply();
					}
					if (attrs.name === 'exp_year' && formController.exp_month.$error.rejected) {
						// by changing the year, we reset a rejected state from month
						formController.exp_month.$setValidity('rejected', true);
						formController.exp_month.$submitted = false;
						scope.$apply();
					}

					// reset payment data
					scope.payment_method.payment_data = null;
				});

				if (attrs.name === 'number') {
					element.on('blur', function(event) {
						var elem = angular.element(this);
						var number = elem.val().replace(/[^0-9]/g, ''), bits = [];
						for (var k = 0; k<number.length; k += 4) {
							bits.push(number.substr(k, 4));
						}
						elem.val(bits.join(' '));
					});
				}
			}
		};
	}]);
});


})();
