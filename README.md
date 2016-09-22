# Stripe Payment Provider Integration for django-shop

This integrates Stripe for django-shop version 0.9 and above.


## Installation

```
pip install djangoshop-stripe
```

In ``settings.py`` of your project

Add ``'shop_stripe'`` to ``INSTALLED_APPS``.

At https:://stripe.com/ create an account and apply for a public/private key-pair. Then add these
keys:

```
SHOP_STRIPE = {
    'PUBKEY': 'pk_<public-key-as-delivered-by-Stripe>',
    'APIKEY': 'sk_<api-key-as-delivered-by-Stripe>',
    'PURCHASE_DESCRIPTION': _("Thanks for purchasing at MyShop"),
}
```

Add ``'shop_stripe.modifiers.StripePaymentModifier'`` to the list of ``SHOP_CART_MODIFIERS``.

Add ``'shop_stripe.payment.OrderWorkflowMixin'`` to the list of ``SHOP_ORDER_WORKFLOWS``.

Locate the projects's folder ``node_modules``; if unsure consult your settings variable
``STATICFILES_DIRS``. Change into it's parent folder and invoke:

```
npm install angular-stripe --save
```

## Changes

### 0.2.1
* django-shop now uses django-angular to load and initialize modules. Adopted here.

### 0.2.0
* Replaced ``bower`` against ``npm``.
* Since Ben Drucker is unwilling to provide an installable AngularJS module,
  it is build and shipped with **djangoshop-stripe**.

### 0.1.4
Fixed Python3 compatibility issue.

### 0.1.3
In django-angular the naming scheme changed. Reflect these changes.

### 0.1.2
Adopted for asynchronous payments as available in django-shop-0.9.0rc2.

### 0.1.1
Initial working release.
