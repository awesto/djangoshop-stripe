# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import stripe
from datetime import date
from django.conf import settings
from django.conf.urls import patterns, url
from django.core.exceptions import ImproperlyConfigured
from django.http.response import HttpResponse, HttpResponseBadRequest
from django.utils.translation import ugettext_lazy as _
from django.utils.six.moves.urllib.parse import urljoin
from shop.models.cart import CartModel
from shop.models.order import BaseOrder, OrderModel, OrderPayment
from shop.payment.base import PaymentProvider
from shop.modifiers.base import PaymentModifier
from django_fsm import transition


class StripePayment(PaymentProvider):
    """
    Provides a payment service for Stripe.
    """
    namespace = 'stripe-payment'

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^charge$', self.charge_view, name='charge'),
            url(r'^save-token$', self.charge_view, name='save-token'),
        )
        return urlpatterns

    def get_payment_request(self, cart, request):
        """
        From the given request, add a snippet to the page.
        """
        js_expression = 'scope.charge().then(function(response) { $window.location.href=response.data.thank_you_url; });'
        return js_expression

    @classmethod
    def save_token_view(cls, request):
        """
        Store the Stripe token in the cart for later usage.
        """
        body = json.loads(request.body)
        cart = CartModel.objects.get_from_request(request)
        cart.payment_method['stripe_token'] = body['token']
        cart.save()

    @classmethod
    def charge_view(cls, request):
        """
        Use the Stripe token from the request and charge immediately.
        """
        stripe.api_key = settings.SHOP_STRIPE['APIKEY']
        body = json.loads(request.body)
        cart = CartModel.objects.get_from_request(request)
        cart.update(request)  # to calculate the total
        try:
            charge = stripe.Charge.create(
                amount=cart.total.as_integer(),
                currency=cart.total.get_currency(),
                source=body['token'],
                description=settings.SHOP_STRIPE['PURCHASE_DESCRIPTION']
            )
            if charge['status'] == 'succeeded':
                order = OrderModel.objects.create_from_cart(cart, request)
                order.add_charge(charge)
                order.save()
                response = {'thank_you_url': OrderModel.objects.get_latest_url()}
                return HttpResponse(json.dumps(response), content_type='application/json;charset=UTF-8')
            return HttpResponseBadRequest(charge)
        except (KeyError, stripe.error.CardError) as err:
            return HttpResponseBadRequest(err)


class StripePaymentModifier(PaymentModifier):
    identifier = StripePayment.namespace
    payment_provider = StripePayment()
    commision_percentage = 3

    def get_choice(self):
        return (self.identifier, _("Credit Card"))

    def add_extra_cart_row(self, cart, request):
        from decimal import Decimal
        from shop.rest.serializers import ExtraCartRow

        if not self.is_active(cart) or not self.commision_percentage:
            return
        amount = cart.subtotal * Decimal(self.commision_percentage / 100.0)
        instance = {'label': _("+ {}% handling fees").format(self.commision_percentage), 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount

    def update_render_context(self, context):
        super(StripePaymentModifier, self).update_render_context(context)
        today = date.today()
        context['payment_modifiers']['month_range'] = \
            [(date(2000, m, 1).strftime('%m'), date(2000, m, 1).strftime('%b')) for m in range(1, 13)]
        context['payment_modifiers']['years_range'] = range(today.year, today.year + 11)
        context['payment_modifiers']['stripe_payment'] = True


class OrderWorkflowMixin(object):
    TRANSITION_TARGETS = {
        'charge_credit_card': _("Paid by Credit Card"),
    }

    def __init__(self, *args, **kwargs):
        if not isinstance(self, BaseOrder):
            raise ImproperlyConfigured('OrderWorkflowMixin is not of type BaseOrder')
        super(OrderWorkflowMixin, self).__init__(*args, **kwargs)

    @transition(field='status', source=['created'], target='charge_credit_card')
    def add_charge(self, charge):
        payment = OrderPayment(order=self, transaction_id=charge['id'], payment_method=StripePayment.namespace)
        assert payment.amount.get_currency() == charge['currency'].upper(), "Currency mismatch"
        payment.amount = charge['amount']
        payment.amount /= payment.amount.subunits
        payment.save()
