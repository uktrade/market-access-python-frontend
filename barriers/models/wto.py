from utils.models import APIModel

import dateutil.parser


class WTOProfile(APIModel):
    """
    Wrapper around API WTO Profile data
    """

    @property
    def status_text(self):
        if self.wto_has_been_notified:
            return "Yes"
        elif self.wto_should_be_notified:
            return "No - this barrier should be notified to the WTO"
        return "No - this barrier should not be notified to the WTO"
