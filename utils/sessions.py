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
        del session['oauth_state_id']
        session['sso_token'] = access_token
        user_synced = sync_user(session)

    return user_synced


class SessionList:
    """
    A list that is stored as a string in the session.
    Can be used to manage lists across views.
    """

    def __init__(self, session, key):
        self.session = session
        self.key = key

    @property
    def value_as_string(self):
        return self.session.get(self.key)

    def append(self, value):
        original_string = self.session.get(self.key)
        if original_string:
            self.value = f"{self.session.get(self.key)},{value}"
        else:
            self.value = str(value)

    def remove(self, value):
        new_list = self.str_to_list(self.value_as_string)
        new_list.remove(str(value))
        self.value = ",".join(new_list)

    @classmethod
    def str_to_list(cls, value):
        if value:
            return value.replace(" ", "").split(",")
        else:
            return []

    @property
    def value(self):
        return self.str_to_list(self.value_as_string)

    @value.setter
    def value(self, value):
        self.session[self.key] = value
