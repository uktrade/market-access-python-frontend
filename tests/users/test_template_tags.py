from django.test import TestCase

from users.templatetags.user_search import update_url_get_parameters


class UsersTemplateTagsTestCase(TestCase):
    def test_update_url_get_parameters(self):
        """
        Examples to test:
            - /foo/?page=3&sort=role&group=1 -> /foo/?page=1&sort=name&group=1
            - /users/?page1&group=all -> /users/?page1&group=all&sort=name
            - /bar/test/?page=3&sort=role&group=1 -> /bar/test/?page=4&sort=role&group=1
        """

        assert (
            update_url_get_parameters(
                "/foo/?page=3&sort=role&group=1", {"page": "1", "sort": "name"}
            )
            == "/foo/?page=1&sort=name&group=1"
        )
        assert (
            update_url_get_parameters("/users/?page=1&group=all", {"sort": "name"})
            == "/users/?page=1&group=all&sort=name"
        )
        assert (
            update_url_get_parameters(
                "/bar/test/?page=3&sort=role&group=1", {"page": "4"}
            )
            == "/bar/test/?page=4&sort=role&group=1"
        )
