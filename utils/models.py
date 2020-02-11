from collections import UserList


class APIModel:
    data = {}

    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        if name in self.data:
            return self.data.get(name)
        raise AttributeError


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
