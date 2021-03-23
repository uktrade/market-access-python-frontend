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


class MentionMarkAllAsRead(View):
    def get(self, request):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.mentions.mark_all_as_read()
        return HttpResponseRedirect("/?active=mentions")


class MentionMarkAllAsUnread(View):
    def get(self, request):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.mentions.mark_all_as_unread()
        return HttpResponseRedirect("/?active=mentions")


class MentionMarkAsReadAndRedirect(View):
    def get(self, request, mention_id):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        mention = client.mentions.get(mention_id)
        client.mentions.mark_as_read(mention_id)
        return HttpResponseRedirect(mention.go_to_url_path)


class TurnNotificationsOffAndRedirect(View):
    def get(self, request):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.notification_exclusion.turn_off_notifications()
        return HttpResponseRedirect("/?active=mentions")


class TurnNotificationsOnAndRedirect(View):
    def get(self, request):
        client = MarketAccessAPIClient(self.request.session.get("sso_token"))
        client.notification_exclusion.turn_on_notifications()
        return HttpResponseRedirect("/?active=mentions")
