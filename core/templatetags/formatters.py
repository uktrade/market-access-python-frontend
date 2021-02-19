from django import template

register = template.Library()


@register.filter
def join_by_comma(iterable, key=None):
    """
    Helper to create a comma separated label out of an iterable.
    :param iterable: an iterable to be joined by comma
    :param key: if the iterable contains dicts, which key would you want to extract
    :return: comma separated string
    """
    if key:
        things_to_join = (item.get(key) for item in iterable)
        return ", ".join(things_to_join)
    else:
        return ", ".join(iterable)
