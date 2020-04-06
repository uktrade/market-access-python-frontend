import operator

from barriers.constants import STATUSES

from utils.metadata import get_metadata
from utils.models import APIModel

import dateutil.parser


class Report(APIModel):
    _metadata = None
    _stages = None
    _progress = None

    @property
    def id(self):
        return self.data.get("id")

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = get_metadata()
        return self._metadata

    @property
    def resolved_text(self):
        if str(self.status) == STATUSES.RESOLVED_IN_FULL:
            return "In full"
        elif str(self.status) == STATUSES.RESOLVED_IN_PART:
            return "In part"
        return "No"

    @property
    def country(self):
        return self.metadata.get_country(self.export_country)

    @property
    def problem_status_text(self):
        return self.metadata.get_problem_status(self.problem_status)

    @property
    def created_on(self):
        return dateutil.parser.parse(self.data['created_on'])

    @property
    def progress(self):
        if self._progress is None:
            self._progress = self.data.get('progress', [])
            self._progress.sort(key=operator.itemgetter('stage_code'))
        return self._progress

    @property
    def is_complete(self):
        for stage in self.progress:
            if stage['status_id'] != 3:
                return False
        return True

    @property
    def next_stage(self):
        for stage in self.progress:
            if stage['status_id'] != 3:
                return stage

    @property
    def stages(self):
        """
        Report stages grouped by main stage number

        Example output:
            {
                '1': {
                    'name': 'Add a barrier,
                    'stages': [
                        {
                            'name': 'Barrier status',
                            'stage_code': '1.1',
                            'status_id': 3,
                            'status_desc': 'COMPLETED'
                        }, {
                            'name': 'Location of the barrier',
                            'stage_code': '1.2',
                            'status_id': 3,
                            'status_desc': 'COMPLETED'
                        }
                    ]
                }
            }
        """
        if self._stages is None:
            base_stages = self.metadata.data.get("report_stages", {})
            progress_lookup = {
                item['stage_code']: item
                for item in self.progress
            }

            self._stages = {}

            for stage_code, name in base_stages.items():
                major_number, minor_number = stage_code.split('.')

                if major_number not in self._stages:
                    self._stages[major_number] = {}

                if minor_number == '0':
                    self._stages[major_number]['name'] = name
                    self._stages[major_number]['stages'] = []
                else:
                    stage = progress_lookup.get(stage_code, {})
                    stage['name'] = name
                    self._stages[major_number]['stages'].append(stage)

        return self._stages
