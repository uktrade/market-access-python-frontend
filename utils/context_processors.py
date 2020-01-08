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


def user_scope(request):
    user = request.session.get("user_data", {})

    extra_context = {
        'user': user,
        'apps': apps(user),
    }

    return extra_context
