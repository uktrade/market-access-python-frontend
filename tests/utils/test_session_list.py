from django.test import TestCase

from utils.sessions import SessionList


class SessionListTestCase(TestCase):
    """
    Test the SessionList class
    """

    def test_append_item(self):
        session = {"wibble": "1"}
        some_list = SessionList(session, "wibble")
        some_list.append(1)
        assert {"wibble": "1,1"} == session

    def test_remove_item(self):
        session = {"wibble": "1,2,3"}
        some_list = SessionList(session, "wibble")
        some_list.remove(1)
        assert {"wibble": "2,3"} == session

    def test_remove_item2(self):
        session = {"wibble": "1,2,3"}
        some_list = SessionList(session, "wibble")
        with self.assertRaisesMessage(ValueError, "list.remove(x): x not in list"):
            some_list.remove(4)

    def test_value_returns_a_list(self):
        session = {"wibble": "1,2,3"}
        some_list = SessionList(session, "wibble")
        assert ["1", "2", "3"] == some_list.value
