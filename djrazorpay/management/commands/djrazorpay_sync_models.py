import os
from typing import Any
from datetime import datetime, timezone

import razorpay
from django.core.management.base import BaseCommand, CommandError, CommandParser
from djrazorpay.models import Customer, Plan, PlanItem, Subscription


class Command(BaseCommand):
    help = "Syncs the database with the latest Razorpay data."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("api_key", type=str)
        parser.add_argument("secret_key", type=str)

    def handle(self, *args: Any, **options: Any) -> str | None:
        api_key: str | None = options.get("api_key", os.environ.get("RAZORPAY_API_KEY"))
        secret_key: str | None = options.get(
            "secret_key", os.environ.get("RAZORPAY_SECRET_KEY")
        )
        if not api_key or not secret_key:
            raise CommandError("Please specify Razorpay secrets correctly.")

        rzp = razorpay.Client(auth=(api_key, secret_key))

        self.sync_plans(rzp)
        self.sync_customers(rzp)
        self.sync_subscriptions(rzp)

    def sync_plans(self, rzp):
        plans = rzp.plan.all()
        for plan_data in plans["items"]:
            item_data = plan_data.pop("item")
            self.stdout.write(f"Sync plan {item_data['id']}")
            item, _ = PlanItem.objects.update_or_create(
                id=item_data["id"],
                defaults={
                    "active": item_data["active"],
                    "name": item_data["name"],
                    "description": item_data["description"],
                    "amount": item_data["amount"] / 100,
                    "unit_amount": item_data["unit_amount"] / 100,
                    "currency": item_data["currency"],
                    "type": item_data["type"],
                    "unit": item_data["unit"],
                    "tax_inclusive": item_data["tax_inclusive"],
                    "hsn_code": item_data["hsn_code"],
                    "sac_code": item_data["sac_code"],
                    "tax_rate": item_data["tax_rate"],
                    "tax_id": item_data["tax_id"],
                    "tax_group_id": item_data["tax_group_id"],
                    "created_at": datetime.fromtimestamp(
                        item_data["created_at"], timezone.utc
                    ),
                    "updated_at": datetime.fromtimestamp(
                        item_data["updated_at"], timezone.utc
                    ),
                },
            )
            Plan.objects.update_or_create(
                id=plan_data["id"],
                defaults={
                    "interval": plan_data["interval"],
                    "period": plan_data["period"],
                    "item": item,
                    "created_at": datetime.fromtimestamp(
                        plan_data["created_at"], timezone.utc
                    ),
                    # "notes": plan_data.get("notes", {}),
                },
            )

    def sync_customers(self, rzp):
        customers = rzp.customer.all()
        for customer_data in customers["items"]:
            self.stdout.write(f"Sync customer {customer_data['id']}")
            Customer.objects.update_or_create(
                id=customer_data["id"],
                defaults={
                    "name": customer_data["name"],
                    "email": customer_data["email"],
                    "contact": customer_data["contact"],
                    "gstin": customer_data["gstin"],
                    "created_at": datetime.fromtimestamp(
                        customer_data["created_at"], timezone.utc
                    ),
                    # "notes": customer_data.get("notes", {}),
                },
            )

    def sync_subscriptions(self, rzp):
        subscriptions = rzp.subscription.all()
        for subscription_data in subscriptions["items"]:
            plan = Plan.objects.get(id=subscription_data["plan_id"])
            try:
                customer = Customer.objects.get(id=subscription_data["customer_id"])
            except Customer.DoesNotExist:
                customer = None
            self.stdout.write(f"Sync subscription {subscription_data['id']}")
            Subscription.objects.update_or_create(
                id=subscription_data["id"],
                defaults={
                    "plan": plan,
                    "customer": customer,
                    "status": subscription_data["status"],
                    "current_start": (
                        datetime.fromtimestamp(
                            subscription_data["current_start"], timezone.utc
                        )
                        if subscription_data["current_start"]
                        else None
                    ),
                    "current_end": (
                        datetime.fromtimestamp(
                            subscription_data["current_end"], timezone.utc
                        )
                        if subscription_data["current_end"]
                        else None
                    ),
                    "ended_at": (
                        datetime.fromtimestamp(
                            subscription_data["ended_at"], timezone.utc
                        )
                        if subscription_data["ended_at"]
                        else None
                    ),
                    "quantity": subscription_data["quantity"],
                    # "notes": subscription_data.get("notes", {}),
                    "charge_at": (
                        datetime.fromtimestamp(
                            subscription_data["charge_at"], timezone.utc
                        )
                        if subscription_data["charge_at"]
                        else None
                    ),
                    "start_at": (
                        datetime.fromtimestamp(
                            subscription_data["start_at"], timezone.utc
                        )
                        if subscription_data["start_at"]
                        else None
                    ),
                    "end_at": (
                        datetime.fromtimestamp(
                            subscription_data["end_at"], timezone.utc
                        )
                        if subscription_data["end_at"]
                        else None
                    ),
                    "auth_attempts": subscription_data["auth_attempts"],
                    "total_count": subscription_data["total_count"],
                    "paid_count": subscription_data["paid_count"],
                    "customer_notify": subscription_data["customer_notify"],
                    "created_at": datetime.fromtimestamp(
                        subscription_data["created_at"], timezone.utc
                    ),
                    "expire_by": (
                        datetime.fromtimestamp(
                            subscription_data["expire_by"], timezone.utc
                        )
                        if subscription_data["expire_by"]
                        else None
                    ),
                    "short_url": subscription_data["short_url"],
                    "has_scheduled_changes": subscription_data["has_scheduled_changes"],
                    "change_scheduled_at": (
                        datetime.fromtimestamp(
                            subscription_data["change_scheduled_at"], timezone.utc
                        )
                        if subscription_data["change_scheduled_at"]
                        else None
                    ),
                    "source": subscription_data["source"],
                    "offer_id": subscription_data["offer_id"],
                    "remaining_count": subscription_data["remaining_count"],
                },
            )
