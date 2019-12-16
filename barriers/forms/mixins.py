class APIFormMixin:
    def __init__(self, id, token, *args, **kwargs):
        self.id = id
        self.token = token
        super().__init__(*args, **kwargs)
