from users.models import User

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
    permitted_keys = [app["key"] for app in user.permitted_applications]

    visible_apps = [app for app in apps if app["permittedKey"] in permitted_keys and app["canShow"]]

    return visible_apps


def user_scope(request):
    client = MarketAccessAPIClient(request.session.get("sso_token"))

    user = User(request.session.get("user_data", {}))
    user.is_stale = True
    user.set_client(client)

    visible_apps = apps(user)
    permitted_keys = [app['permittedKey'] for app in visible_apps]
    if 'datahub-crm' in permitted_keys:
        user.has_crm_permission = True
    else:
        user.has_crm_permission = False

    extra_context = {
        'current_user': user,
        'apps': visible_apps,
    }

    return extra_context
