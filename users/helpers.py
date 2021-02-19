from utils.api.client import MarketAccessAPIClient
from utils.exceptions import APIException


def sync_user(session):
    """
    Calls to /whoami and updates the session
    :param session: Django session instance
    :return: BOOL - whether the sync process was considered successful or not
    """
    synced = False
    token = session.get("sso_token")

    if token:
        client = MarketAccessAPIClient(token)

        # Ref of user_data as of 2020/01/06
        #   id - INT
        #   username - STR
        #   last_login - STR
        #   first_name - STR
        #   last_name - STR
        #   email - STR
        #   location - STR
        #   internal - BOOL
        #   user_profile - DICT
        #       watchList - DICT
        #   permitted_applications - LIST

        try:
            user = client.users.get_current()
            user_data = user.data
        except APIException:
            user_data = {}

        if user_data:
            synced = True
        session["user_data"] = user_data

    return synced
