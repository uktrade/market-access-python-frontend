class APIFormMixin:
    def __init__(self, id, *args, **kwargs):
        self.id = id
        super().__init__(*args, **kwargs)
