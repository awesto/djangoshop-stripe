# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from distutils.version import LooseVersion

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _

from django_fsm import transition, RETURN_VALUE
from rest_framework.exceptions import ValidationError
import stripe

from shop import __version__ as SHOP_VERSION
from shop.models.order import BaseOrder, OrderModel, OrderPayment
from shop.money import MoneyMaker
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
            self.charge(cart, request)
            thank_you_url = OrderModel.objects.get_latest_url()
            js_expression = 'window.location.href="{}";'.format(thank_you_url)
            return js_expression
        except (KeyError, stripe.error.StripeError) as err:
            raise ValidationError(err)

    def charge(self, cart, request):
        """
        Use the Stripe token from the request and charge immediately.
        This view is invoked by the Javascript function `scope.charge()` delivered
        by `get_payment_request`.
        """
        token_id = cart.extra['payment_extra_data']['token_id']
        if LooseVersion(SHOP_VERSION) < LooseVersion('0.11'):
            charge = stripe.Charge.create(
                amount=cart.total.as_integer(),
                currency=cart.total.currency,
                source=token_id,
                description=settings.SHOP_STRIPE['PURCHASE_DESCRIPTION']
            )
            if charge['status'] == 'succeeded':
                order = OrderModel.objects.create_from_cart(cart, request)
                order.add_stripe_payment(charge)
                order.save()
        else:
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
                order.save()

        if charge['status'] != 'succeeded':
            msg = "Stripe returned status '{status}' for id: {id}"
            raise stripe.error.InvalidRequestError(msg.format(**charge))


class OrderWorkflowMixin(object):
    TRANSITION_TARGETS = {
        'paid_with_stripe': _("Paid using Stripe"),
    }

    def __init__(self, *args, **kwargs):
        if not isinstance(self, BaseOrder):
            raise ImproperlyConfigured("class 'OrderWorkflowMixin' is not of type 'BaseOrder'")

        super(OrderWorkflowMixin, self).__init__(*args, **kwargs)

    @transition(field='status', source=['created'], target='paid_with_stripe')
    def add_stripe_payment(self, charge):
        assert self.currency == charge['currency'].upper(), "Currency mismatch"
        Money = MoneyMaker(self.currency)
        amount = Money(charge['amount']) / Money.subunits
        OrderPayment.objects.create(order=self, amount=amount, transaction_id=charge['id'],
                                    payment_method=StripePayment.namespace)

    def is_fully_paid(self):
        return super(OrderWorkflowMixin, self).is_fully_paid()

    @transition(field='status', source='paid_with_stripe', conditions=[is_fully_paid],
                custom=dict(admin=True, button_name=_("Acknowledge Payment")))
    def acknowledge_stripe_payment(self):
        self.acknowledge_payment()

    def refund_payment(self):
        """
        Refund the payment using Stripe's refunding API.
        """
        Money = MoneyMaker(self.currency)
        filter_kwargs = {
            'transaction_id__startswith': 'ch_',
            'payment_method': StripePayment.namespace,
        }
        for payment in self.orderpayment_set.filter(**filter_kwargs):
            refund = stripe.Refund.create(charge=payment.transaction_id)
            if refund['status'] == 'succeeded':
                amount = Money(refund['amount']) / Money.subunits
                OrderPayment.objects.create(order=self, amount=-amount, transaction_id=refund['id'],
                                            payment_method=StripePayment.namespace)

        del self.amount_paid  # to invalidate the cache
        if self.amount_paid:
            # proceed with other payment service providers
            super(OrderWorkflowMixin, self).refund_payment()
