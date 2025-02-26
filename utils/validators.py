import datetime

from django.core.exceptions import ValidationError


def validate_date_not_in_future(value):
    if value > datetime.date.today():
        raise ValidationError(
            "Resolution date must be this month or in the past",
            params={"value": value},
        )


def validate_proposed_estimated_resolution_date(value):
    reference = datetime.date.today().replace(day=1)

    if value < reference:
        raise ValidationError(
            "Date must be this month or in the future",
            params={"value": value},
        )
