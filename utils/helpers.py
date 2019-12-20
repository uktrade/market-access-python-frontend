from urllib.parse import urlsplit

from django.conf import settings
from django.urls import reverse


def build_absolute_uri(request, reverse_path):
    redirect_uri = request.build_absolute_uri(
        reverse(reverse_path)
    )
    uri_bits = urlsplit(redirect_uri)
    if settings.DJANGO_ENV != "local" and uri_bits.scheme != "https":
        redirect_uri = f"{'https'}://{uri_bits.netloc}{uri_bits.path}"

    return redirect_uri
