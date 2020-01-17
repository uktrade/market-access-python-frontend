class APIException(Exception):
    def __init__(self, http_exception):
        self.status_code = http_exception.response.status_code


class DataHubException(Exception):
    pass


class HawkException(Exception):
    pass


class FileUploadError(Exception):
    pass


class ScanError(Exception):
    pass
