from enum import Enum
from typing import Any


class RazorpayStrEnum(str, Enum):
    @classmethod
    def choices(cls) -> list[tuple[Any, str]]:
        return [(key.value, key.name) for key in cls]


class SubscriptionStatus(RazorpayStrEnum):
    """
    The state of Subscription in its lifecycle.
    Ref: https://razorpay.com/docs/payments/subscriptions/states/
    """

    CREATED = "created"
    AUTHENTICATED = "authenticated"
    ACTIVE = "active"
    PENDING = "pending"
    HALTED = "halted"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class PlanPeriod(RazorpayStrEnum):
    """Defines the frequency of the plan."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
