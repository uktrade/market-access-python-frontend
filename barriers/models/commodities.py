from utils.models import APIModel


def format_commodity_code(code):
    code = code.rstrip("0")
    if len(code) % 2:
        code = f"{code}0"
    pairs = [code[i:i + 2] for i in range(0, len(code), 2)]
    if len(pairs) > 2:
        pairs = [pairs[0] + pairs[1]] + pairs[2:]
    return ".".join(pairs)


class Commodity(APIModel):
    """
    A commodity containing a code and description
    """
    def create_barrier_commodity(self, code, country_id):
        return BarrierCommodity({
            "commodity": self.data,
            "code": code,
            "country": {"id": country_id},
        })

    @property
    def code_display(self):
        return format_commodity_code(self.code)

    def to_dict(self):
        return {
            "code": self.code,
            "code_display": self.code_display,
            "description": self.description,
            "full_description": self.full_description,
        }


class BarrierCommodity(APIModel):
    """
    A commodity associated to a barrier containing a specific code and country
    """
    _commodity = None

    @property
    def commodity(self):
        if self._commodity is None:
            self._commodity = Commodity(self.data.get("commodity"))
        return self._commodity

    @property
    def code_display(self):
        return format_commodity_code(self.code)

    def to_dict(self):
        return {
            "code": self.code,
            "code_display": self.code_display,
            "country": self.country,
            "commodity": self.commodity.to_dict()
        }
