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


def user_scope(request):
    user = get_user(request)
    return {"current_user": user}


def feature_flags(request):
    return {
        "feature_flags": {
            "action_plans_enabled": settings.ACTION_PLANS_ENABLED,
        }
    }
