from django.views.generic import RedirectView

from utils.api_client import MarketAccessAPIClient


class DownloadDocument(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        client = MarketAccessAPIClient(self.request.session.get('sso_token'))
        document_id = self.kwargs.get('document_id')
        data = client.documents.get_download(document_id)
        return data['document_url']
