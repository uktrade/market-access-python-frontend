from users.helpers import sync_user


def init_session(session, access_token):
    """
    Initialise a session as part of the user login journey.
    :param session: django session instance
    :param access_token: bearer token from SSO
    :return: BOOL - whether the init process was considered successful or not
    """
    user_synced = False

    if access_token:
        del session["oauth_state_id"]
        session["sso_token"] = access_token
        user_synced = sync_user(session)

    return user_synced
