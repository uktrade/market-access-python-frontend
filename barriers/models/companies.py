from utils.models import APIModel

import dateutil.parser


class Company(APIModel):
    """
    Wrapper around API company data
    """

    def __init__(self, data):
        self.data = data
        self.created_on = dateutil.parser.parse(data["created_on"])

    def get_address_display(self):
        address_parts = [
            self.data["address"].get("line_1"),
            self.data["address"].get("line_2"),
            self.data["address"].get("town"),
            self.data["address"].get("county"),
            self.data["address"].get("postcode"),
            self.data["address"].get("country", {}).get("name"),
        ]
        address_parts = [part for part in address_parts if part]
        return ", ".join(address_parts)
