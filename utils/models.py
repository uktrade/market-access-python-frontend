from collections import UserList
from typing import Dict, Tuple

import dateutil.parser


class APIModel:
    data: Dict = {}
    date_fields: Tuple = tuple()

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        if name not in self.data:
            raise AttributeError(f"{name} not found in data")

        value = self.data.get(name)
        if not value:
            return value

        if name in self.date_fields:
            return dateutil.parser.parse(value)

        return value


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
