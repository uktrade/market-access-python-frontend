from urllib.parse import urlparse

from django.http import Http404
from django.urls import resolve


class Referer:
    """
    Wrapper for http referer information
    """

    def __init__(self, current_path, referer_path):
        self.current_path = current_path
        self.referer_path = referer_path
        self.current_url_name = self.get_url_name(current_path)
        if referer_path:
            self.referer_url_name = self.get_url_name(referer_path)
        else:
            self.referer_url_name = None

    def get_url_name(self, path):
        try:
            return resolve(urlparse(path).path).url_name
        except Http404:
            return None

    @property
    def path(self):
        if self.referer_url_name != self.current_url_name:
            return self.referer_path

    @property
    def url_name(self):
        return self.referer_url_name


class RefererMixin:
    """
    Allows a view to access the referring url information
    """

    _referer = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        context_data["referer"] = self.referer
        return context_data

    def get_referer(self):
        if "referer_path" in self.request.POST:
            referer_path = self.request.POST.get("referer_path")
        elif self.request.META.get("HTTP_REFERER"):
            referer_path = urlparse(self.request.META.get("HTTP_REFERER")).path
            referer_querystring = urlparse(self.request.META.get("HTTP_REFERER")).query
            if referer_querystring:
                referer_path = f"{referer_path}?{referer_querystring}"
        else:
            referer_path = None

        return Referer(
            current_path=self.request.path_info,
            referer_path=referer_path,
        )

    @property
    def referer(self):
        if self._referer is None:
            self._referer = self.get_referer()
        return self._referer
