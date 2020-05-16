# Changes

## 1.2 (recommended for django-SHOP version 1.2)
* Add support for Django-3.0.
* Drop support for Python-2.
* Drop support for Django-2.0 and lower.

## 1.0
* Adopted for django-SHOP version 1.0.

## 0.12.3
* The Stripe credit card form, now uses the same validation techniques as all the other forms
  in the checkout process.

## 0.12 / 0.12.2 (don't use 0.12.1)
* Switch to django-SHOP versioning scheme, so that versions are in sync.
* Adopted to django-angular version 2.0.
* Add support for payment refundings.

## 0.3.3, 0.3.4
* Added compatibility on creating and populating Order for django-SHOP-0.11.

## 0.3.2
* Fixed: Initialize scope of Angular directive `stripe-card-form` even for missing
  `data` object.

## 0.3.1
* Fixed: Compute amount in correct currency using Order object instead of defaulting.

## 0.3.0
* Upgrade to ``stripe`` version 1.53 and ``angular-stripe`` version 4.2.13.

## 0.2.2
* Replace ``{% addtoblock "ext-js" %}`` against ``{% addtoblock "js" %}``, since Django-SHOP 0.10.0
  can handle externally referenced files as well.

## 0.2.1
* Adopted for django-SHOP version 0.10. Do not use this version for Django-SHOP 0.9.x.
* Stripe form template can be used by static views, rendering the PaymentMethodForm manually.

## 0.2.0
* Replaced ``bower`` against ``npm``.
* Replaced Sekizai block ``shop-ng-requires`` against ``ng-requires``.
* Replaced Sekizai block ``shop-ng-config`` against ``ng-config``.
* Since Ben Drucker is [unwilling](https://github.com/bendrucker/angular-stripe/issues/50) to
  provide an installable ``angular-stripe.js`` module, it is build and shipped with
  **djangoshop-stripe**.

## 0.1.4
Fixed Python3 compatibility issue.

## 0.1.3
In django-angular the naming scheme changed. Reflect these changes.

## 0.1.2
Adopted for asynchronous payments as available in django-shop-0.9.0rc2.

## 0.1.1
Initial working release.
