def public_view(func):
    """
    Decorator for public views that do not require authentication
    """
    orig_func = func
    orig_func._public_view = True

    return func
