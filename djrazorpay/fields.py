import datetime
import warnings
from typing import Any

from django.conf import settings
from django.core import exceptions
from django.db import models
from django.utils import timezone


class RazorpayEntityIdField(models.CharField):
    description = "Stores the Razorpay-assigned ID to an entity"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["max_length"] = 64
        super().__init__(*args, **kwargs)


class RazorpayDateTimeField(models.DateTimeField):
    description = "Accepts Razorpay timestamps which are UTC timestamps (integer)."

    def to_python(self, value: Any) -> Any:
        if value is None:
            return value
        if isinstance(value, datetime.datetime):
            return value
        if isinstance(value, datetime.date):
            value = datetime.datetime(value.year, value.month, value.day)
            if settings.USE_TZ:
                # For backwards compatibility, interpret naive datetimes in
                # local time. This won't work during DST change, but we can't
                # do much about it, so we let the exceptions percolate up the
                # call stack.
                try:
                    name = f"{self.model.__name__}.{self.name}"
                except AttributeError:
                    name = "(unbound)"
                warnings.warn(
                    f"DateTimeField {name} received a naive datetime ({value}) while "
                    "time zone support is active.",
                    RuntimeWarning,
                )
                default_timezone = datetime.timezone.utc
                value = timezone.make_aware(value, default_timezone)
            return value

        try:
            parsed = datetime.datetime.fromtimestamp(value, datetime.timezone.utc)
            if parsed is not None:
                return parsed
        except ValueError:
            raise exceptions.ValidationError(
                self.error_messages["invalid_datetime"],
                code="invalid_datetime",
                params={"value": value},
            )
