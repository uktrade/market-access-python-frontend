import json
import sys

sys.path.append(".")
from utils.metadata import get_metadata


class UpdateMetadata:

    def __init__(self, metadata):
        self.metadata = metadata

    def update_file(self, key, updated_value):
        # Get the existing metadata
        with open("core/fixtures/metadata.json", "r") as file:
            data = json.load(file)

        data.update({key: updated_value})

        # Overwrite file with new data
        with open("core/fixtures/metadata.json", "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def update_barrier_tags(self):
        tags = self.metadata.get_barrier_tags()
        ordered_tags = sorted(tags, key=lambda k: k["order"])

        self.update_file(key="barrier_tags", updated_value=ordered_tags)


metadata = UpdateMetadata(metadata=get_metadata())
metadata.update_barrier_tags()
