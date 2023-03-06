from urllib.parse import urlsplit

from django.conf import settings
from django.urls import reverse


def build_absolute_uri(request, reverse_path):
    redirect_uri = request.build_absolute_uri(reverse(reverse_path))
    uri_bits = urlsplit(redirect_uri)
    if settings.DJANGO_ENV != "local" and uri_bits.scheme != "https":
        redirect_uri = f"{'https'}://{uri_bits.netloc}{uri_bits.path}"

    return redirect_uri


def remove_empty_values_from_dict(dictionary):
    return {k: v for k, v in dictionary.items() if v}


def format_dict_for_url_querystring(filters_list, filter_names_to_format):
    # Using URLencode on a sub-dictionary leads to incorrectly formatted
    # querystrings - need to convert the sub-dictionary to a string so it
    # can be correctly converted.
    for filter_name in filter_names_to_format:
        if filter_name in filters_list:
            if type(filters_list[filter_name]) is dict:
                filters_list[filter_name] = str(filters_list[filter_name])
                filters_list[filter_name] = filters_list[filter_name].replace("'", '"')

    return filters_list
