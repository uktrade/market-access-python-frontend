import requests

from utils.api_client import MarketAccessAPIClient
from utils.exceptions import FileUploadError


class APIFormMixin:
    def __init__(self, id, token, *args, **kwargs):
        self.id = id
        self.token = token
        super().__init__(*args, **kwargs)


class DocumentMixin:
    """
    Helper functions to upload the 'document' field of a form.

    1. Calls the API with file name and size, getting back a document id
       and signed url for uploading to S3.
    2. Uploads the file to S3.
    3. Calls the API confirming that the file has been uploaded.
    4. Polls the API until the virus scan is complete, raising an exception
       if it fails the check.
    """
    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token')
        super().__init__(*args, **kwargs)

    def upload_document(self):
        document = self.cleaned_data['document']

        client = MarketAccessAPIClient(self.token)
        data = client.documents.create(
            filename=document.name,
            filesize=document.size,
        )
        document_id = data['id']

        self.upload_to_s3(url=data['signed_upload_url'], document=document)

        client.documents.complete_upload(document_id)
        client.documents.check_scan_status(document_id)

        return {
            "id": document_id,
            "file": {
                "name": document.name,
                "size": document.size,
            }
        }

    def upload_to_s3(self, url, document):
        document.seek(0)
        response = requests.put(
            url,
            headers={
                'x-amz-server-side-encryption': 'AES256',
            },
            data=document
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise FileUploadError(
                "A system error has occured, so the file has not been "
                "uploaded. Try again."
            )
