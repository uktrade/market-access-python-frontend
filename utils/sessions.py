from users.helpers import sync_user
# from utils.api_client import MarketAccessAPIClient


def init_session(session, access_token):
    """
    Initialise a session as part of the user login journey.
    :param session: django session instance
    :param access_token: bearer token from SSO
    :return: BOOL - whether the init process was considered successful or not
    """
    user_synced = False

    if access_token:
        del session['oauth_state_id']
        session['sso_token'] = access_token
        user_synced = sync_user(session)
        # client = MarketAccessAPIClient(access_token)
        #
        # # sync user
        # # Ref of user_data as of 2020/01/06
        # #   id - INT
        # #   username - STR
        # #   last_login - STR
        # #   first_name - STR
        # #   last_name - STR
        # #   email - STR
        # #   location - STR
        # #   internal - BOOL
        # #   user_profile - DICT
        # #       watchList - DICT
        # #   permitted_applications - LIST
        #
        # # user_data = session['api_client'].get('whoami') or {}
        # user_data = client.get('whoami') or {}
        # if user_data:
        #     init_successful = True
        # session['user_data'] = user_data

    return user_synced
