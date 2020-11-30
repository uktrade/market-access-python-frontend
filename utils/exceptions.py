from json.decoder import JSONDecodeError
import logging


logger = logging.getLogger(__name__)


class APIException(Exception):
    pass


class APIHttpException(APIException):
    def __init__(self, http_error, response=None):
        self.status_code = http_error.response.status_code
        self.message = str(http_error)
        self.response_data = None

        if response:
            try:
                self.response_data = response.json()
            except JSONDecodeError:
                pass
        logging.warning(f"APIHttpException: {self.message}")


class APIJsonException(APIException):
    def __init__(self, message):
        self.message = message
        logging.warning(f"APIJsonException: {self.message}")


class DataHubException(Exception):
    pass


class HawkException(Exception):
    pass


class FileUploadError(Exception):
    pass


class ScanError(Exception):
    pass
