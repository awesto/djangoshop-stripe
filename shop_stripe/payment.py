from django.conf import settings
from django.utils.text import format_lazy
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
import stripe
from shop.models.order import OrderModel
from shop.payment.providers import PaymentProvider

stripe.api_key = settings.SHOP_STRIPE['APIKEY']


class StripePayment(PaymentProvider):
    """
    Provides a payment service for Stripe.
    """
    namespace = 'stripe-payment'

    def get_payment_request(self, cart, request):
        """
        From the given request, add a snippet to the page.
        """
        try:
            order = self.charge(cart, request)
            js_expression = 'window.location.href="{}";'.format(order.get_absolute_url())
            return js_expression
        except stripe.error.StripeError as err:
            raise ValidationError(err._message)
        except KeyError as err:
            raise ValidationError(str(err))

    def charge(self, cart, request):
        """
        Use the Stripe token from the request and charge immediately.
        This view is invoked by the Javascript function `scope.charge()` delivered
        by `get_payment_request`.
        """
        token_id = cart.extra['payment_extra_data'].get('token_id')
        if not token_id:
            message = _("Stripe payment token is missing")
            raise stripe.error.StripeError(message)

        order = OrderModel.objects.create_from_cart(cart, request)
        charge = stripe.Charge.create(
            amount=cart.total.as_integer(),
            currency=cart.total.currency,
            source=token_id,
            transfer_group=order.get_number(),
            description=settings.SHOP_STRIPE['PURCHASE_DESCRIPTION'],
        )
        if charge['status'] == 'succeeded':
            order.populate_from_cart(cart, request)
            order.add_stripe_payment(charge)
            order.save(with_notification=True)
        else:
            message = _("Stripe returned status '{status}' for id: {id}")
            raise stripe.error.StripeError(format_lazy(message, **charge))
        return order
