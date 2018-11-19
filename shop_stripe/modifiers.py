# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import date
from django.utils.translation import ugettext_lazy as _
from shop.payment.modifiers import PaymentModifier
from .payment import StripePayment


class StripePaymentModifier(PaymentModifier):
    identifier = StripePayment.namespace
    payment_provider = StripePayment()
    commision_percentage = None

    def get_choice(self):
        return (self.identifier, _("Credit Card"))

    def is_disabled(self, cart):
        return cart.total == 0

    def add_extra_cart_row(self, cart, request):
        from decimal import Decimal
        from shop.serializers.cart import ExtraCartRow

        if not self.is_active(cart) or not self.commision_percentage:
            return
        amount = cart.total * Decimal(self.commision_percentage / 100.0)
        instance = {'label': _("+ {}% handling fee").format(self.commision_percentage), 'amount': amount}
        cart.extra_rows[self.identifier] = ExtraCartRow(instance)
        cart.total += amount

    def update_render_context(self, context):
        super(StripePaymentModifier, self).update_render_context(context)
        today = date.today()
        context['payment_modifiers']['month_range'] = \
            [(date(2000, m, 1).strftime('%m'), date(2000, m, 1).strftime('%b')) for m in range(1, 13)]
        context['payment_modifiers']['years_range'] = range(today.year, today.year + 11)
        context['payment_modifiers']['stripe_payment'] = True
