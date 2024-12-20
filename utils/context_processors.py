from django.conf import settings
from django.core.cache import cache

from users.models import User
from utils.api.client import MarketAccessAPIClient


def get_user(request):
    user_id = request.session.get("user_data", {}).get("id")
    if not user_id:
        return

    cache_key = f"user_data:{user_id}"
    user_data = cache.get(cache_key)
    if user_data is not None:
        return User(user_data)

    client = MarketAccessAPIClient(request.session.get("sso_token"))
    return client.users.get_current()


def get_mention_counts(request):
    sso_token = request.session.get("sso_token")
    if not sso_token:
        return

    client = MarketAccessAPIClient(sso_token)
    resource = client.user_mention_counts.get()
    unread_count = resource.total - resource.read_by_recipient
    counts = {
        "total": resource.total,
        "read_by_recipient": resource.read_by_recipient,
        "display_count": unread_count if unread_count <= 99 else "99+",
    }
    return counts


def user_scope(request):
    user = get_user(request)

    return {
        "current_user": user,
    }


def user_mention_counts(request):
    counts = get_mention_counts(request)

    return {
        "user_mention_counts": counts,
    }


def feature_flags(request):
    return {
        "feature_flags": {
            "action_plans_enabled": settings.ACTION_PLANS_ENABLED,
            "new_action_plans_enabled": settings.NEW_ACTION_PLANS_ENABLED,
        }
    }
