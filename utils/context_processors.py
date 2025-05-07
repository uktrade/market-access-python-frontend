import logging

from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

from users.models import User
from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIHttpException

logger = logging.getLogger(__name__)


def get_user(request):
    user_id = request.session.get("user_data", {}).get("id")
    if not user_id:
        return

    cache_key = f"user_data:{user_id}"
    user_data = cache.get(cache_key)
    if user_data is not None:
        return User(user_data)

    client = MarketAccessAPIClient(request.session.get("sso_token"))
    try:
        user = client.users.get_current()
        return user
    except APIHttpException as e:
        if e.status_code == 401:
            return reverse("users:login")
        else:
            raise


def get_mention_counts(request):
    sso_token = request.session.get("sso_token")
    if not sso_token:
        return

    counts = {"total": None, "read_by_recipient": None, "display_count": None}
    client = MarketAccessAPIClient(sso_token)

    try:
        resource = client.user_mention_counts.get()
        unread_count = resource.total - resource.read_by_recipient
        counts["total"] = resource.total
        counts["read_by_recipient"] = resource.read_by_recipient
        counts["display_count"] = unread_count if unread_count <= 99 else "99+"
    except APIHttpException as e:
        logger.warning(f"get_mention_counts.exception: {e.__dict__}")
        if e.status_code == 401:
            return reverse("users:login")

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
