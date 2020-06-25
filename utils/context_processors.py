from utils.api.client import MarketAccessAPIClient


class Domains:
    DATA_HUB = "https://www.datahub.trade.gov.uk/"
    MI = "https://mi.exportwins.service.trade.gov.uk/"
    FIND_EXPORTERS = "https://find-exporters.datahub.trade.gov.uk/"
    MARKET_ACCESS = "https://market-access.trade.gov.uk/"


def apps(user):
    apps = [
        {
            'name': 'Companies',
            'permittedKey': 'datahub-crm',
            'activeKey': 'datahub-companies',
            'canShow': True,
            'href': (Domains.DATA_HUB + 'companies')
        },
        {
            'name': 'Contacts',
            'permittedKey': 'datahub-crm',
            'activeKey': 'datahub-contacts',
            'canShow': True,
            'href': (Domains.DATA_HUB + 'contacts')
        },
        {
            'name': 'Events',
            'permittedKey': 'datahub-crm',
            'activeKey': 'datahub-events',
            'canShow': True,
            'href': (Domains.DATA_HUB + 'events')
        },
        {
            'name': 'Interactions',
            'permittedKey': 'datahub-crm',
            'activeKey': 'datahub-interactions',
            'canShow': True,
            'href': (Domains.DATA_HUB + 'interactions')
        },
        {
            'name': 'Investments',
            'permittedKey': 'datahub-crm',
            'activeKey': 'datahub-investments',
            'canShow': True,
            'href': (Domains.DATA_HUB + 'investments')
        },
        {
            'name': 'Orders',
            'permittedKey': 'datahub-crm',
            'activeKey': 'datahub-orders',
            'canShow': True,
            'href': (Domains.DATA_HUB + 'omis')
        },
        {
            'name': 'Dashboards',
            'permittedKey': 'datahub-mi',
            'activeKey': 'datahub-mi',
            'canShow': True,
            'href': Domains.MI
        },
        {
            'name': 'Find exporters',
            'permittedKey': 'find-exporters',
            'activeKey': 'find-exporters',
            'canShow': True,
            'href': Domains.FIND_EXPORTERS
        },
        {
            'name': 'Market Access',
            'permittedKey': 'market-access',
            'activeKey': 'market-access',
            'canShow': True,
            'href': Domains.MARKET_ACCESS
        },
    ]

    # Find out which of the apps the user have access to
    permitted_applications = user.get("permitted_applications", [])
    permitted_keys = [app["key"] for app in permitted_applications]

    visible_apps = [app for app in apps if app["permittedKey"] in permitted_keys and app["canShow"]]

    return visible_apps


class LazyPermissionsFetcher:
    _permissions = None

    def __init__(self, token):
        self.token = token

    def permissions(self):
        if self._permissions is None:
            self._permissions = self.get_permissions()
        return self._permissions

    def get_permissions(self):
        client = MarketAccessAPIClient(self.token)
        user_data = client.get("whoami")
        return user_data.get("permissions", [])


def user_scope(request):
    user = request.session.get("user_data", {})
    visible_apps = apps(user)
    permitted_keys = [app['permittedKey'] for app in visible_apps]
    if 'datahub-crm' in permitted_keys:
        user['has_crm_permission'] = True
    else:
        user['has_crm_permission'] = False

    token = request.session.get("sso_token")
    extra_context = {
        'current_user': user,
        'apps': visible_apps,
        'user_permissions': LazyPermissionsFetcher(token).permissions
    }

    return extra_context
