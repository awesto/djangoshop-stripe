from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _
from django_fsm import transition
import stripe
from shop.models.order import BaseOrder, OrderPayment
from shop.money import MoneyMaker
from shop_stripe.payment import StripePayment


class OrderWorkflowMixin:
    TRANSITION_TARGETS = {
        'paid_with_stripe': _("Paid using Stripe"),
    }

    def __init__(self, *args, **kwargs):
        if not isinstance(self, BaseOrder):
            raise ImproperlyConfigured("class 'OrderWorkflowMixin' is not of type 'BaseOrder'")

        super().__init__(*args, **kwargs)

    @transition(field='status', source=['created'], target='paid_with_stripe')
    def add_stripe_payment(self, charge):
        assert self.currency == charge['currency'].upper(), "Currency mismatch"
        Money = MoneyMaker(self.currency)
        amount = Money(charge['amount']) / Money.subunits
        OrderPayment.objects.create(
            order=self,
            amount=amount,
            transaction_id=charge['id'],
            payment_method=StripePayment.namespace,
        )

    def is_fully_paid(self):
        return super().is_fully_paid()

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
                OrderPayment.objects.create(
                    order=self,
                    amount=-amount,
                    transaction_id=refund['id'],
                    payment_method=StripePayment.namespace,
                )

        del self.amount_paid  # to invalidate the cache
        if self.amount_paid:
            # proceed with other payment service providers
            super().refund_payment()

    def cancelable(self):
        return super().cancelable() or self.status in ['paid_with_stripe']
