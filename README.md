# Stripe Payment Provider Integration for django-shop

This integrates the Stripe for django-shop version 1.0 and above.


## Installation

for django-shop version 1.0.x:

```
pip install djangoshop-stripe<1.1
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

