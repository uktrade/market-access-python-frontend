from http import HTTPStatus

from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from django.views.generic import FormView, RedirectView

from utils.api.client import MarketAccessAPIClient
from utils.exceptions import FileUploadError, ScanError


class DownloadDocument(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        document_id = self.kwargs.get("document_id")
        data = client.documents.get_download(document_id)
        return data["document_url"]


class AddDocumentAjaxView(FormView):
    """
    Base ajax view for uploading documents
    """

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["token"] = self.request.session.get("sso_token")
        return kwargs

    def form_valid(self, form):
        try:
            document = form.save()
        except FileUploadError as e:
            return JsonResponse(
                {"message": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
        except ScanError as e:
            return JsonResponse({"message": str(e)}, status=HTTPStatus.UNAUTHORIZED,)

        self.add_document_to_session(document)

        return JsonResponse(
            {
                "documentId": document["id"],
                "delete_url": self.get_delete_url(document),
                "file": {
                    "name": document["file"]["name"],
                    "size": filesizeformat(document["file"]["size"]),
                },
            }
        )

    def get_session_key(self):
        raise NotImplementedError

    def get_delete_url(self, document):
        raise NotImplementedError

    def add_document_to_session(self, document):
        session_key = self.get_session_key()
        documents = self.request.session.get(session_key, [])
        documents.append(
            {
                "id": document["id"],
                "name": document["file"]["name"],
                "size": document["file"]["size"],
            }
        )
        self.request.session[session_key] = documents

    def form_invalid(self, form):
        return JsonResponse(
            {"message": ", ".join(form.errors.get("document", [])),},
            status=HTTPStatus.BAD_REQUEST,
        )


class DeleteDocumentAjaxView(RedirectView):
    """
    Base view for deleting a document from the session.

    Can be called via ajax or as a get request.
    """

    def get_session_key(self):
        raise NotImplementedError

    def delete_document_from_session(self):
        document_id = str(self.kwargs.get("document_id"))
        session_key = self.get_session_key()
        documents = self.request.session[session_key]

        self.request.session[session_key] = [
            document for document in documents if document["id"] != document_id
        ]

    def get(self, request, *args, **kwargs):
        self.delete_document_from_session()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.delete_document_from_session()
        return JsonResponse({})
