import datetime

from django.core.exceptions import ValidationError


def validate_date_not_in_future(value):
    if value > datetime.date.today():
        raise ValidationError(
            "Resolution date must be this month or in the past",
            params={"value": value},
        )


def validate_date_is_in_future(value):
    if value < datetime.date.today():
        raise ValidationError(
            "Date must be this month or in the future",
            params={"value": value},
        )
