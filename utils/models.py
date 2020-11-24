from collections import UserList

import dateutil.parser


class APIModel:
    data = {}
    date_fields = tuple()

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        if name in self.data:
            value = self.data.get(name)
            if value and name in self.date_fields:
                return dateutil.parser.parse(value)
            return value
        raise AttributeError(f"{name} not found in data")


class ModelList(UserList):
    """
    A list of objects from the API.

    Also stores the count from the API for use in pagination.
    """

    def __init__(self, model, data, total_count):
        self.model = model
        self.data = data
        self.total_count = total_count

    def __iter__(self):
        for obj in self.data:
            yield self.model(obj)
