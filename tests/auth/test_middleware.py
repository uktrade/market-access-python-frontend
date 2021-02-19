from django.http import HttpResponse
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import path, reverse
from django.views.generic import View

from authentication.decorators import public_view
from config.urls import urlpatterns as orig_urlpatterns


@public_view
class PublicView(View):
    """Views with public_view decorator are public"""

    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, World!")


class RegularView(View):
    """Regular views are all protected by SSO middleware"""

    def get(self, request, *args, **kwargs):
        return HttpResponse("Hello, World!")


urlpatterns = orig_urlpatterns + [
    path("test-public/", PublicView.as_view(), name="test_public"),
    path("test-protected/", RegularView.as_view(), name="test_protected"),
]


@override_settings(ROOT_URLCONF=__name__)
class TestSSOMiddleware(TestCase):
    def setUp(self):
        self.anonymous_client = Client()

    def test_public_view_bypasses_sso(self):
        url = reverse("test_public")
        response = self.client.get(url)
        assert response.status_code == 200

    def test_regular_view_is_protected(self):
        url = reverse("test_protected")
        redirect_url = reverse("users:login")
        response = self.client.get(url)
        assert response.status_code == 302
        assert response.url == redirect_url
