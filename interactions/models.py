from utils.metadata import get_metadata, Statuses
from utils.models import APIModel

import dateutil.parser


class Interaction(APIModel):
    def __init__(self, data):
        self.data = data
        self.is_note = True
        self.modifier = 'note'
        self.date = dateutil.parser.parse(data['created_on'])
        self.text = data['text']
        self.user = data['created_by']
        self.documents = [Document(document) for document in data['documents']]

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
        }


class HistoryItem(APIModel):
    def __init__(self, data):
        self.data = data
        metadata = get_metadata()

        if data['field'] == 'status':
            self.is_status = True,
            self.modifier = 'status'
            self.date = dateutil.parser.parse(data['date'])
            self.event = data['field_info']['event']
            self.state = {
                'from': metadata.get_status_text(data['old_value']),
                'to': metadata.get_status_text(
                    data['new_value'],
                    data['field_info'].get('sub_status'),
                    data['field_info'].get('sub_status_other'),
                ),
                'date': dateutil.parser.parse(
                    data['field_info']['status_date']
                ),
                'is_resolved': data['new_value'] in (
                    Statuses.RESOLVED_IN_PART,
                    Statuses.RESOLVED_IN_FULL,
                ),
                'show_summary': data['new_value'] in (
                    Statuses.OPEN_IN_PROGRESS,
                    Statuses.UNKNOWN,
                    Statuses.OPEN_PENDING_ACTION,
                ),
            }
            self.text = data['field_info']['status_summary']
            self.user = data['user']
        elif data['field'] == 'priority':
            self.is_priority = True
            self.modifier = 'priority'
            self.date = dateutil.parser.parse(data['date'])
            self.priority = metadata.get_priority(data['new_value'])
            self.text = data['field_info']['priority_summary']
            self.user = data['user']
        else:
            self.is_assessment = True
            self.is_edit = data['old_value'] is not None
            self.name = metadata.get_assessment_name(data['field'])
            self.date = dateutil.parser.parse(data['date'])
            self.user = data['user']


class Document(APIModel):
    def __init__(self, data):
        self.data = data
        self.id = data['id']
        self.name = data['name']
        self.size = data['size']
        self.can_download = data['status'] == 'virus_scanned'
        self.status = data['status']

    @property
    def readable_status(self):
        return {
            'not_virus_scanned': 'Not virus scanned',
            'virus_scanning_scheduled': 'Virus scanning scheduled',
            'virus_scanning_in_progress': 'Virus scanning in progress',
            'virus_scanning_failed': 'Virus scanning failed.',
            'virus_scanned': 'Virus scanned',
            'deletion_pending': 'Deletion pending',
        }.get(self.status)
