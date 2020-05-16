from django.conf import settings


def public_keys(request):
    return {
        'SHOP_STRIPE_PUBKEY': settings.SHOP_STRIPE['PUBKEY'],
        'SHOP_STRIPE_PREFILL': getattr(settings, 'SHOP_STRIPE_PREFILL', False)
    }
