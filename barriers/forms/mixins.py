import requests

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import FileUploadError, ScanError


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
        self.token = kwargs.pop("token")
        super().__init__(*args, **kwargs)

    def validate_document(self, field_name="document"):
        """
        Only uploads files when javascript is disabled
        """
        document = self.cleaned_data.get(field_name)
        document_id_field_name = self.get_document_id_field_name(field_name)
        multi_value = hasattr(self.fields.get(document_id_field_name), "choices")

        if document:
            try:
                uploaded_document = self.upload_document(field_name)
                if multi_value:
                    document_ids = self.cleaned_data.get(document_id_field_name, [])
                    document_ids.append(uploaded_document["id"])
                    self.cleaned_data[document_id_field_name] = document_ids
                else:
                    self.cleaned_data[document_id_field_name] = uploaded_document["id"]
            except FileUploadError as e:
                self.add_error(field_name, str(e))
            except ScanError as e:
                self.add_error(field_name, str(e))
        return document

    def get_document_id_field_name(self, field_name):
        if f"{field_name}_id" in self.fields:
            return f"{field_name}_id"
        elif f"{field_name}_ids" in self.fields:
            return f"{field_name}_ids"

    def upload_document(self, field_name="document"):
        document = self.cleaned_data[field_name]

        client = MarketAccessAPIClient(self.token)
        data = client.documents.create(filename=document.name, filesize=document.size,)
        document_id = data["id"]

        self.upload_to_s3(url=data["signed_upload_url"], document=document)

        client.documents.complete_upload(document_id)
        client.documents.check_scan_status(document_id)

        return {
            "id": document_id,
            "file": {"name": document.name, "size": document.size,},
        }

    def upload_to_s3(self, url, document):
        document.seek(0)
        response = requests.put(
            url, headers={"x-amz-server-side-encryption": "AES256",}, data=document
        )
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise FileUploadError(
                "A system error has occured, so the file has not been "
                "uploaded. Try again."
            )

    def is_multi_document(self):
        """
        Is the submitted field a multi document field
        """
        for field_name, field in self.fields.items():
            if self.cleaned_data.get(field_name):
                return field.multi_document
