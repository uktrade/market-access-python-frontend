import math

from django.conf import settings


class PaginationMixin:
    """
    Allows views to get pagination data
    """
    def get_current_page(self):
        page = self.request.GET.get('page', 1)
        try:
            return max(1, int(page))
        except ValueError:
            return 1

    def update_querystring(self, **kwargs):
        params = self.request.GET.copy()
        params.pop('page', None)
        params.update(kwargs)
        return params.urlencode()

    def get_pagination_data(
        self,
        object_list,
        limit=settings.API_RESULTS_LIMIT
    ):
        total_pages = math.ceil(object_list.total_count / limit)
        current_page = self.get_current_page()
        pagination_data = {
            'total_pages': total_pages,
            'current_page': current_page,
            'pages': [
                {
                    'label': i,
                    'url': self.update_querystring(page=i),
                }
                for i in range(1, total_pages + 1)
            ]
        }
        if current_page > 1:
            pagination_data['previous'] = self.update_querystring(
                page=current_page-1
            )

        if current_page != total_pages:
            pagination_data['next'] = self.update_querystring(
                page=current_page+1
            )

        return pagination_data
