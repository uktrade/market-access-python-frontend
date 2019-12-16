from urllib.parse import urlencode
import uuid

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import RedirectView

import requests


class Login(RedirectView):
    def get(self, request, *args, **kwargs):
        self.state_id = str(uuid.uuid4())
        request.session['oauth_state_id'] = self.state_id
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        params = {
            'response_type': 'code',
            'client_id': settings.SSO_CLIENT,
            'redirect_uri': self.request.build_absolute_uri(
                reverse('users:login_callback')
            ),
            'state': self.state_id,
        }
        if settings.SSO_MOCK_CODE:
            params['code'] = settings.SSO_MOCK_CODE

        return f"{settings.SSO_AUTHORIZE_URI}?{urlencode(params)}"


class LoginCallback(RedirectView):
    """
    Use the code in the querystring to get a token from the SSO server.

    If using Docker, this call comes from within the container, so
    SSO_TOKEN_URI has to be the internal address 'mocksso'.
    This is different to SSO_AUTHORIZE_URI, which is used in the browser, so
    has to be an external address.
    Because of this difference, we cannot easily use django-authbroker-client
    which assumes the same domain for both addresses.
    """
    def get(self, request, *args, **kwargs):
        state_id = request.session.get('oauth_state_id')
        if not state_id:
            return HttpResponseRedirect(reverse('users:login'))

        response = requests.post(
            url=settings.SSO_TOKEN_URI,
            json={
                'code': request.GET.get('code'),
                'grant_type': 'authorization_code',
                'client_id': settings.SSO_CLIENT,
                'client_secret': settings.SSO_SECRET,
                'redirect_uri': request.build_absolute_uri(
                    reverse('users:login_callback')
                ),
            },
        )
        response_data = response.json()

        if response_data.get('access_token'):
            request.session['sso_token'] = response_data['access_token']
            del request.session['oauth_state_id']
            return HttpResponseRedirect(self.get_redirect_url())
        else:
            raise Exception("No access_token from SSO")

        return super().get(request, *args, **kwargs)

    def get_redirect_url(self):
        url = self.request.session.get('return_path')
        if url:
            del self.request.session['return_path']
            return url
        return reverse('barriers:dashboard')
