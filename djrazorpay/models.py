import datetime

from django.db import models

from djrazorpay.enums import PlanPeriod, SubscriptionStatus
from djrazorpay.fields import RazorpayDateTimeField, RazorpayEntityIdField


class RazorpayBaseModel(models.Model):
    id: str = RazorpayEntityIdField(primary_key=True)
    created_at: datetime = RazorpayDateTimeField(null=False)

    class Meta:
        abstract = True


class PlanItem(RazorpayBaseModel):
    active = models.BooleanField()
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    unit_amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=4)
    type = models.CharField(max_length=16)
    unit = models.CharField(max_length=16, null=True)
    tax_inclusive = models.BooleanField()
    hsn_code = models.CharField(max_length=16, null=True)
    sac_code = models.CharField(max_length=16, null=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    tax_id = models.CharField(max_length=32, null=True)
    tax_group_id = models.CharField(max_length=32, null=True)
    updated_at = RazorpayDateTimeField(null=False)


class Plan(RazorpayBaseModel):
    interval = models.IntegerField()
    period = models.CharField(
        max_length=16,
        choices=PlanPeriod.choices(),
        help_text="Defines the frequency of the plan.",
    )
    item = models.OneToOneField(PlanItem, on_delete=models.CASCADE)
    # notes = models.JSONField()


class Customer(RazorpayBaseModel):
    name = models.CharField(max_length=64)
    email = models.CharField(max_length=64)
    contact = models.CharField(max_length=16)
    gstin = models.CharField(max_length=16, null=True)
    # notes = models.JSONField()


class Subscription(RazorpayBaseModel):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=SubscriptionStatus.choices())
    current_start = RazorpayDateTimeField(null=True)
    current_end = RazorpayDateTimeField(null=True)
    ended_at = RazorpayDateTimeField(null=True)
    quantity = models.IntegerField()
    # notes = models.JSONField()
    charge_at = RazorpayDateTimeField(null=True)
    start_at = RazorpayDateTimeField(null=True)
    end_at = RazorpayDateTimeField(null=True)
    auth_attempts = models.IntegerField()
    total_count = models.IntegerField()
    paid_count = models.IntegerField()
    customer_notify = models.BooleanField()
    expire_by = RazorpayDateTimeField(null=True)
    short_url = models.URLField()
    has_scheduled_changes = models.BooleanField()
    change_scheduled_at = RazorpayDateTimeField(null=True)
    source = models.CharField(max_length=16)
    offer_id = models.CharField(max_length=32, null=True)
    remaining_count = models.IntegerField()
