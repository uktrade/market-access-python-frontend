import logging


class RequestLoggingMiddleware:
    """
    Middleware to make a log record of each url request with logged in user
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logging.info(
            f"Request Log: '{request.method}' call for '{request.path}' by use '{request.user}'"
        )

        return self.get_response(request)
