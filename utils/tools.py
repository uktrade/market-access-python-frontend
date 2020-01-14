def nested_sort(obj):
    """
    Sort a dict/list and all it's values recursively
    """
    if isinstance(obj, dict):
        return sorted((k, nested_sort(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(nested_sort(x) for x in obj)
    else:
        return obj
