import math

from django.conf import settings


class PaginationMixin:
    """
    Allows views to get pagination data
    """

    pagination_limit = settings.API_RESULTS_LIMIT

    def get_current_page(self):
        page = self.request.GET.get("page", 1)
        try:
            return max(1, int(page))
        except ValueError:
            return 1

    def update_querystring(self, **kwargs):
        params = self.request.GET.copy()
        params.pop("page", None)
        params.update(kwargs)
        return params.urlencode()

    def get_pagination_data(self, object_list):
        limit = self.get_pagination_limit()
        total_count = object_list.total_count
        total_pages = math.ceil(total_count / limit)
        current_page = self.get_current_page()
        start_position = ((current_page - 1) * limit) + 1
        # this used min(), but that crashes the tests because a MagicMock object can't handle the < operator
        full_page_end = start_position + limit - 1
        end_position = (
            full_page_end + total_count - abs(total_count - full_page_end)
        ) // 2
        pagination_data = {
            "total_pages": total_pages,
            "current_page": current_page,
            "pages": [
                {
                    "label": i,
                    "url": self.update_querystring(page=i),
                }
                for i in range(1, total_pages + 1)
            ],
            "total_items": total_count,
            "start_position": start_position,
            "end_position": end_position,
        }
        if current_page > 1:
            pagination_data["previous"] = self.update_querystring(page=current_page - 1)

        if current_page != total_pages:
            pagination_data["next"] = self.update_querystring(page=current_page + 1)

        return self.truncate_pagination_data(pagination_data)

    def get_pagination_limit(self):
        return self.pagination_limit

    def get_pagination_offset(self):
        return self.get_pagination_limit() * (self.get_current_page() - 1)

    def truncate_pagination_data(self, pagination_data, block_size=4):
        """
        Truncate the pagination links.

        We don't want to show a link for every page if there are hundreds of
        pages. This trims out page links we're probably not interested in.

        This is a direct port from the node project.
        """
        pages = pagination_data["pages"]

        if len(pages) <= block_size:
            return pagination_data

        current_page_num = pagination_data["current_page"]
        current_page_index = pagination_data["current_page"] - 1
        first_page = pages[0]
        last_page = pages[-1]

        block_pivot = int(block_size / 2)
        start_of_current_block = abs(current_page_num - block_pivot)
        start_of_last_block = last_page["label"] - block_size
        block_start_index = min(
            start_of_current_block,
            start_of_last_block,
            current_page_index,
        )

        truncated_pages = pages[block_start_index:][:block_size]
        first_of_truncated_pages_num = truncated_pages[0]["label"]
        last_of_truncated_pages_num = truncated_pages[-1]["label"]

        if first_of_truncated_pages_num > 3:
            truncated_pages = [{"label": "..."}] + truncated_pages

        if first_of_truncated_pages_num == 3:
            truncated_pages = [pages[1]] + truncated_pages

        if first_of_truncated_pages_num > 1:
            truncated_pages = [first_page] + truncated_pages

        if last_of_truncated_pages_num < last_page["label"] - 2:
            truncated_pages.append({"label": "..."})

        if last_of_truncated_pages_num == last_page["label"] - 2:
            truncated_pages.append(pages[-2])

        if last_of_truncated_pages_num < last_page["label"]:
            truncated_pages.append(last_page)

        pagination_data["pages"] = truncated_pages
        return pagination_data
