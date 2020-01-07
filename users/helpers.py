from utils.api_client import MarketAccessAPIClient


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

        user_data = client.get('whoami') or {}
        if user_data:
            synced = True
        session['user_data'] = user_data

    return synced
