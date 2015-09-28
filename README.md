# Stripe Payment Provider Integration for django-shop

This integrates Stripe for django-shop version 0.3 and above.


## Installation

In ``settings.py`` add ``'shop_stripe'`` to ``INSTALLED_APPS``.

In ``settings.py`` add

```
SHOP_STRIPE = {
    'PUBKEY': 'pk_<public-key-as-delivered-by-Stripe>',
    'APIKEY': 'sk_<api-key-as-delivered-by-Stripe>',
    'PURCHASE_DESCRIPTION': _("Thanks for purchasing at MyShop"),
}
```
