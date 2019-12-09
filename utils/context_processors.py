def permitted_applications(request):
    datahubDomain = "https://www.datahub.trade.gov.uk/"
    miDomain = 'https://mi.exportwins.service.trade.gov.uk/'
    findExportersDomain = 'https://find-exporters.datahub.trade.gov.uk/'
    marketAccessDomain = 'https://market-access.trade.gov.uk/'
    return {
        'user': {
            'username': 'Mark',
            'id': 48,
            'permitted_applications': [
                {
                    'key': 'datahub-crm',
                },
                {
                    'key': 'market-access',
                }
            ]
        },
        'apps': [
            {
                'permittedKey': 'datahub-crm',
                'activeKey': 'datahub-companies',
                'canShow': True,
                'name': 'Companies',
                'href': (datahubDomain + 'companies')
            }, {
                'permittedKey': 'datahub-crm',
                'activeKey': 'datahub-contacts',
                'canShow': True,
                'name': 'Contacts',
                'href': (datahubDomain + 'contacts')
            }, {
                'permittedKey': 'datahub-crm',
                'activeKey': 'datahub-events',
                'canShow': True,
                'name': 'Events',
                'href': (datahubDomain + 'events')
            }, {
                'permittedKey': 'datahub-crm',
                'activeKey': 'datahub-interactions',
                'canShow': True,
                'name': 'Interactions',
                'href': (datahubDomain + 'interactions')
            }, {
                'permittedKey': 'datahub-crm',
                'activeKey': 'datahub-investments',
                'canShow': True,
                'name': 'Investments',
                'href': (datahubDomain + 'investments')
            }, {
                'permittedKey': 'datahub-crm',
                'activeKey': 'datahub-orders',
                'canShow': True,
                'name': 'Orders',
                'href': (datahubDomain + 'omis')
            }, {
                'permittedKey': 'datahub-mi',
                'activeKey': 'datahub-mi',
                'canShow': True,
                'name': 'Dashboards',
                'href': miDomain
            }, {
                'permittedKey': 'find-exporters',
                'activeKey': 'find-exporters',
                'canShow': True,
                'name': 'Find exporters',
                'href': findExportersDomain
            }, {
                'permittedKey': 'market-access',
                'activeKey': 'market-access',
                'canShow': True,
                'name': 'Market Access',
                'href': marketAccessDomain
            }
        ]
    }
