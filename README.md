# Stripe Payment Provider Integration for django-shop

This integrates the Stripe for django-shop version 0.9 and above.


## Installation

for django-shop version 0.9.x:

```
pip install djangoshop-stripe==0.1.4
```

for django-shop version 0.10.x:

```
pip install djangoshop-stripe==0.2.0
```

## Configuration

In ``settings.py`` of the merchant's project:

Add ``'shop_stripe'`` to ``INSTALLED_APPS``.

At [Stripe](https://stripe.com/) create an account and apply for a public/private key-pair. Then add
these keys:

```
SHOP_STRIPE = {
    'PUBKEY': 'pk_<public-key-as-delivered-by-Stripe>',
    'APIKEY': 'sk_<api-key-as-delivered-by-Stripe>',
    'PURCHASE_DESCRIPTION': _("Thanks for purchasing at MyShop"),
}
```

Add ``'shop_stripe.modifiers.StripePaymentModifier'`` to the list of ``SHOP_CART_MODIFIERS``.

Add ``'shop_stripe.payment.OrderWorkflowMixin'`` to the list of ``SHOP_ORDER_WORKFLOWS``.

Add ``'shop_stripe.context_processors.public_keys'`` to the list of template
``OPTIONS['context_processors']``


## Changes

### 0.2.2
* Replace ``{% addtoblock "ext-js" %}`` against ``{% addtoblock "js" %}``, since Django-SHOP 0.10.0
  can handle externally referenced files as well.


### 0.2.1
* Adopted for django-SHOP version 0.10. Do not use this version for Django-SHOP 0.9.x.
* Stripe form template can be used by static views, rendering the PaymentMethodForm manually.

### 0.2.0
* Replaced ``bower`` against ``npm``.
* Replaced Sekizai block ``shop-ng-requires`` against ``ng-requires``.
* Replaced Sekizai block ``shop-ng-config`` against ``ng-config``.
* Since Ben Drucker is [unwilling](https://github.com/bendrucker/angular-stripe/issues/50) to
  provide an installable ``angular-stripe.js`` module, it is build and shipped with
  **djangoshop-stripe**.

### 0.1.4
Fixed Python3 compatibility issue.

### 0.1.3
In django-angular the naming scheme changed. Reflect these changes.

### 0.1.2
Adopted for asynchronous payments as available in django-shop-0.9.0rc2.

### 0.1.1
Initial working release.
