from utils.models import APIModel


class FeatureFlag(APIModel):
    """
    Wrapper around API Feature Flag data
    """
    _name = None

    @property
    def name(self):
        return self.data["name"]
