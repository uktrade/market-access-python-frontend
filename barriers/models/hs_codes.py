from utils.models import APIModel


class HSCode(APIModel):

    @property
    def code_display(self):
        pairs = [self.code[i:i+2] for i in range(0, len(self.code), 2)]
        return ".".join(pairs)
