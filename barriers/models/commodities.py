from utils.models import APIModel


class Commodity(APIModel):

    @property
    def code_display(self):
        pairs = [self.code[i:i+2] for i in range(0, len(self.code), 2)]
        return ".".join(pairs)

    def to_dict(self):
        return {
            "code": self.code,
            "code_display": self.code_display,
            "description": self.description,
            "full_description": self.full_description,
        }
