import datetime

import dateutil.parser
from django.template import Library
from django.template.defaultfilters import stringfilter

register = Library()


@register.filter
@stringfilter
def parse_date(date_string, format):
    """
    Return a datetime corresponding to date_string, parsed according to format.

    For example, to re-display a date string in another format::

        {{ "01/01/1970"|parse_date:"%m/%d/%Y"|date:"F jS, Y" }}

    """
    try:
        return datetime.datetime.strptime(date_string, format)
    except ValueError:
        return None


@register.filter
@stringfilter
def parse_iso(date_string):
    return dateutil.parser.parse(date_string)
