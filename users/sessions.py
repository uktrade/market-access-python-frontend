from django.contrib.sessions.backends.db import SessionStore as DBStore

from utils.api_client import MarketAccessAPIClient


class SessionStore(DBStore):
    """
    Custom Session Engine with convenience functions for user data
    """
    def get_watchlists(self):
        try:
            return self['user_data']['user_profile']['watchList'].get(
                'lists', []
            )
        except KeyError:
            return []

    def set_watchlists(self, watchlists):
        self['user_data']['user_profile']['watchList']['lists'] = watchlists
        client = MarketAccessAPIClient(self['sso_token'])
        client.users.patch(user_profile=self['user_data']['user_profile'])
        self.save()

    def delete_watchlist(self, index):
        watchlists = self.get_watchlists()
        if index < len(watchlists):
            del watchlists[index]
            self.set_watchlists(watchlists)
