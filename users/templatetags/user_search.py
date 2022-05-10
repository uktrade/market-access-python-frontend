from typing import Dict
from urllib.parse import parse_qs, urlencode, urlparse

from django import template

register = template.Library()


def update_url_get_parameters(url_path, parameters_to_update: Dict[str, str]):
    """
    Update the url with the given parameters
    and remove unwanted parameters.

    example:
    update_url_get_parameters("/foo/?page=3&sort=role&group=1", {"page": "1", "sort": "name"})

    would return: /foo/?page=1&sort=name&group=1
    """
    url_get_params = parse_qs(urlparse(url_path).query)
    updated_get_params = {**url_get_params, **parameters_to_update}
    return f"{urlparse(url_path).path}?{urlencode(updated_get_params, doseq=True)}"


# django template tag that returns the 'users' url with the given parameters
@register.simple_tag()
def updated_user_search_url(current_path, **parameters):
    # return current_path with updated parameters
    return update_url_get_parameters(current_path, parameters)
