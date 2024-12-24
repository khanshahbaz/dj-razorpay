import os
from typing import Any

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
                    "created_at": item_data["created_at"],
                    "updated_at": item_data["updated_at"],
                },
            )
            Plan.objects.update_or_create(
                id=plan_data["id"],
                defaults={
                    "interval": plan_data["interval"],
                    "period": plan_data["period"],
                    "item": item,
                    "created_at": plan_data["created_at"],
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
                    "created_at": customer_data["created_at"],
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
                    "current_start": subscription_data["current_start"],
                    "current_end": subscription_data["current_end"],
                    "ended_at": subscription_data["ended_at"],
                    "quantity": subscription_data["quantity"],
                    # "notes": subscription_data.get("notes", {}),
                    "charge_at": subscription_data["charge_at"],
                    "start_at": subscription_data["start_at"],
                    "end_at": subscription_data["end_at"],
                    "auth_attempts": subscription_data["auth_attempts"],
                    "total_count": subscription_data["total_count"],
                    "paid_count": subscription_data["paid_count"],
                    "customer_notify": subscription_data["customer_notify"],
                    "created_at": subscription_data["created_at"],
                    "expire_by": subscription_data["expire_by"],
                    "short_url": subscription_data["short_url"],
                    "has_scheduled_changes": subscription_data["has_scheduled_changes"],
                    "change_scheduled_at": subscription_data["change_scheduled_at"],
                    "source": subscription_data["source"],
                    "offer_id": subscription_data["offer_id"],
                    "remaining_count": subscription_data["remaining_count"],
                },
            )
