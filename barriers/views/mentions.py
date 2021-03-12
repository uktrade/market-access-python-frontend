from django.http import HttpResponseRedirect
from django.views.generic.base import View
from utils.api.client import MarketAccessAPIClient


class MentionMarkAsRead(View):
    def get(self, request, mention_id):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.mentions.mark_as_read(mention_id)
        return HttpResponseRedirect("/?active=mentions")


class MentionMarkAsUnread(View):
    def get(self, request, mention_id):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.mentions.mark_as_unread(mention_id)
        return HttpResponseRedirect("/?active=mentions")
