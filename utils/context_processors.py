from django.conf import settings
from django.core.cache import cache

from users.models import User
from utils.api.client import MarketAccessAPIClient


def get_user(request):
    user_id = request.session.get("user_data", {}).get("id")
    if user_id:
        cache_key = f"user_data:{user_id}"
        user_data = cache.get(cache_key)
        if user_data is not None:
            return User(user_data)

        client = MarketAccessAPIClient(request.session.get("sso_token"))
        return client.users.get_current()


def new_mentions_count(request):
    client = MarketAccessAPIClient(request.session.get("sso_token"))
    mentions = client.mentions.list()
    new_mentions_count = len(
        [mention for mention in mentions if not mention.read_by_recipient]
    )
    if new_mentions_count > 99:
        return "99+"
    else:
        return new_mentions_count


def user_scope(request):
    user = get_user(request)
    count = new_mentions_count(request)
    return {
        "current_user": user,
        "new_mentions_count": count,
    }


def feature_flags(request):
    return {
        "feature_flags": {
            "action_plans_enabled": settings.ACTION_PLANS_ENABLED,
            "new_action_plans_enabled": settings.NEW_ACTION_PLANS_ENABLED,
        }
    }
