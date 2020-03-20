from utils.diff import diff_match_patch
from utils.metadata import get_metadata
from utils.models import APIModel

import dateutil.parser


class BaseHistoryItem(APIModel):
    _metadata = None
    _new_value = None
    _old_value = None

    @property
    def date(self):
        return dateutil.parser.parse(self.data["date"])

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def new_value(self):
        if self._new_value is None:
            self._new_value = self.get_value(self.data["new_value"]) or ""
        return self._new_value

    @property
    def old_value(self):
        if self._old_value is None:
            self._old_value = self.get_value(self.data["old_value"]) or ""
        return self._old_value

    @property
    def diff(self):
        dmp = diff_match_patch()
        diffs = dmp.diff_main(self.old_value, self.new_value)
        dmp.diff_cleanupSemantic(diffs)
        return dmp.diff_prettyHtml(diffs)

    def get_value(self, value):
        return value
