from datetime import datetime

from reports.constants import FormSessionKeys
from reports.forms.new_report_barrier_location import HasAdminAreas
from reports.forms.new_report_barrier_sectors import SectorsAffected
from reports.forms.new_report_barrier_status import BarrierStatuses
from utils.api.client import MarketAccessAPIClient


# Barrier fields and the corresponding step in the "Add a barrier" journey.
# fields = (
#     "id",
#     "code",
#     "problem_status",       # Step 1.1 - Status
#     "is_resolved",          # Step 1.2 - Status
#     "resolved_date",        # Step 1.2 - Status
#     "resolved_status",      # Step 1.2 - Status
#     # ==============================
#     "status",               # n/a - Barrier status (e.g.: unfinished, open , dormant, etc...)
#     "status_summary",       # this is set in step 5 - without this the draft barrier cannot be submitted (MAR-221)
#     "status_date",          # n/a
#     # ==============================
#     "export_country",       # Step 2 - Location - UUID
#     "country_admin_areas",  # Step 2 - Location - LIST of UUIDS
#     # ==============================
#     "sectors_affected",     # Step 3 - Sectors - BOOL
#     "all_sectors",          # Step 3 - Sectors - BOOL
#     "sectors",              # Step 3 - Sectors - LIST of UUIDS
#     # ==============================
#     "product",              # Step 4 - About - STR
#     "source",               # Step 4 - About - STR
#     "other_source",         # Step 4 - About - STR
#     "barrier_title",        # Step 4 - About - STR
#     "tags"                  # Step 4 - About - LIST of IDS
#     # ==============================
#     "problem_description",  # Step 5 - Summary - STR
#     "next_steps_summary",   # Step 5 - Summary - STR
#     # ==============================
#     "progress",             # n/a
#     "created_by",           # n/a
#     "created_on",           # n/a
#     "modified_by",          # n/a
#     "modified_on",          # n/a
# )


class SessionKeys:
    """
    Set of session keys to be used at report forms to help with draft barrier data management.
    """
    meta_mapping = {
        FormSessionKeys.PROBLEM_STATUS: "problem_status_form_data",
        FormSessionKeys.STATUS: "status_form_data",
        FormSessionKeys.LOCATION: "location_form_data",
        FormSessionKeys.HAS_ADMIN_AREAS: "has_admin_areas_form_data",
        FormSessionKeys.ADMIN_AREAS: "admin_areas_form_data",
        FormSessionKeys.SELECTED_ADMIN_AREAS: "selected_admin_areas",
        FormSessionKeys.SECTORS_AFFECTED: "sectors_affected",
        FormSessionKeys.SECTORS: "sectors",
        FormSessionKeys.ABOUT: "about",
        FormSessionKeys.SUMMARY: "summary",

    }
    attr_mapping = {}

    @classmethod
    def __init__(cls, infix=""):
        """Set up session key mapping to reflect context."""
        for key, value in cls.meta_mapping.items():
            new_value = f"draft_barrier_{infix}_{value}"
            setattr(cls, key, new_value)
            cls.attr_mapping[key] = new_value

    @classmethod
    def flush(cls, session):
        """Removes session keys as per mapping."""
        for key, value in cls.attr_mapping.items():
            session.pop(value, None)


class ReportFormGroup:
    """
    Used to handle field values for draft barriers.
    Form values are stored in the user session:
     - session key naming pattern for DRAFT barriers: "draft_barrier_<UUID>_session_key"
     - session key naming pattern for UNSAVED barriers: "draft_barrier__session_key"
    """
    def __init__(self, session, barrier_id=None):
        self.session = session
        self.session_keys = None
        self.barrier = None
        self.barrier_id = barrier_id
        self.client = MarketAccessAPIClient(session.get("sso_token"))
        self.init_session_keys()

    # STATUS
    # ==================================
    @property
    def problem_status_form(self):
        return self.get(FormSessionKeys.PROBLEM_STATUS, {})

    @problem_status_form.setter
    def problem_status_form(self, value):
        self.set(FormSessionKeys.PROBLEM_STATUS, value)

    @property
    def status_form(self):
        return self.get(FormSessionKeys.STATUS, {})

    @status_form.setter
    def status_form(self, value):
        self.set(FormSessionKeys.STATUS, value)

    # LOCATION
    # ==================================
    @property
    def location_form(self):
        return self.get(FormSessionKeys.LOCATION, {})

    @location_form.setter
    def location_form(self, value):
        self.set(FormSessionKeys.LOCATION, value)

    @property
    def has_admin_areas(self):
        return self.get(FormSessionKeys.HAS_ADMIN_AREAS, {})

    @has_admin_areas.setter
    def has_admin_areas(self, value):
        self.set(FormSessionKeys.HAS_ADMIN_AREAS, value)

    @property
    def selected_admin_areas(self):
        """
        Selected admin areas
        :return: STR - comma separated UUIDs
        """
        return self.get(FormSessionKeys.SELECTED_ADMIN_AREAS, "")

    @selected_admin_areas.setter
    def selected_admin_areas(self, value):
        self.set(FormSessionKeys.SELECTED_ADMIN_AREAS, value)

    @property
    def selected_admin_areas_as_list(self):
        areas_list = []
        areas = self.selected_admin_areas

        if areas:
            areas_list = areas.replace(" ", "").split(",")

        return areas_list

    def remove_selected_admin_area(self, admin_area_id):
        admin_areas = self.selected_admin_areas_as_list
        admin_areas.remove(admin_area_id)
        self.selected_admin_areas = ', '.join(admin_areas)

    # SECTORS
    # ==================================
    @property
    def sectors_affected(self):
        return self.get(FormSessionKeys.SECTORS_AFFECTED, {})

    @sectors_affected.setter
    def sectors_affected(self, value):
        self.set(FormSessionKeys.SECTORS_AFFECTED, value)

    @property
    def selected_sectors(self):
        """
        Selected sectors
        :return: STR - comma separated UUIDs
        """
        return self.get(FormSessionKeys.SECTORS, "")

    @selected_sectors.setter
    def selected_sectors(self, value):
        self.set(FormSessionKeys.SECTORS, value)

    @property
    def selected_sectors_as_list(self):
        sectors = self.selected_sectors
        if sectors:
            sectors = sectors.replace(" ", "").split(",")
        return sectors or []

    def selected_sectors_generator(self, metadata):
        """
        Returns selected sectors if any as a GENERATOR.

        :metadata: data from utils.metadata.get_metadata()
        :return: TUPLE, (BOOL|has selected sectors, GENERATOR|selected sectors)
        """
        sector_ids = self.selected_sectors
        if sector_ids == "all":
            sectors = (("all", "All sectors"),)
        else:
            sectors = (
                (sector["id"], sector["name"])
                for sector in metadata.get_sectors(sector_ids)
            )
        return (sector_ids != ""), sectors

    def remove_selected_sector(self, sector_id):
        sectors = self.selected_sectors_as_list
        sectors.remove(sector_id)
        self.selected_sectors = ', '.join(sectors)

    # ABOUT
    # ==================================
    @property
    def about_form(self):
        return self.get(FormSessionKeys.ABOUT, {})

    @about_form.setter
    def about_form(self, value):
        self.set(FormSessionKeys.ABOUT, value)

    # SUMMARY
    # ==================================
    @property
    def summary_form(self):
        return self.get(FormSessionKeys.SUMMARY, {})

    @summary_form.setter
    def summary_form(self, value):
        self.set(FormSessionKeys.SUMMARY, value)

    # UTILS
    # ==================================
    @property
    def session_key_infix(self):
        infix = ""
        if self.barrier_id:
            infix = str(self.barrier_id)
        return infix

    def load_from_session(self):
        pass

    def get(self, session_key, default=None):
        """Retrieving the value stored in a session key"""
        if not session_key:
            # If for whatever reason the session_key is falsy fall back to default
            return default

        key = getattr(self.session_keys, session_key)
        return self.session.get(key, default)

    def set(self, session_key, value):
        """Assigning a value to a session key"""
        if not session_key:
            return

        key = getattr(self.session_keys, session_key)
        if key:
            self.session[key] = value

    def flush_session_keys(self):
        if self.session_keys:
            self.session_keys.flush(self.session)

    def init_session_keys(self):
        self.flush_session_keys()
        self.session_keys = SessionKeys(self.session_key_infix)

    def get_problem_status_form_data(self):
        return {
            "status": str(self.barrier.data.get("problem_status"))
        }

    def get_status_form_data(self):
        """Returns DICT - extract status form data from barrier.data"""
        data = {
            "status": "",
            "resolved_month": None,
            "resolved_year": None,
            "part_resolved_month": None,
            "part_resolved_year": None,
            "is_resolved": None,
        }

        if not self.barrier:
            return data

        data["is_resolved"] = self.barrier.data.get("is_resolved")
        data["status"] = str(self.barrier.data.get("resolved_status"))

        if data["status"] in (BarrierStatuses.RESOLVED, BarrierStatuses.PARTIALLY_RESOLVED):
            date_string = self.barrier.data.get("resolved_date")
            if date_string:
                date = datetime.strptime(date_string, '%Y-%m-%d')
                if data["status"] == BarrierStatuses.RESOLVED:
                    data["resolved_month"] = date.month
                    data["resolved_year"] = date.year
                elif data["status"] == BarrierStatuses.PARTIALLY_RESOLVED:
                    data["part_resolved_month"] = date.month
                    data["part_resolved_year"] = date.year
        else:
            data["status"] = BarrierStatuses.UNRESOLVED

        return data

    def get_location_form_data(self):
        return {
            "country": self.barrier.data.get("export_country")
        }

    def get_has_admin_areas_form_data(self):
        data = {"has_admin_areas": None}
        if self.barrier.data["country_admin_areas"]:
            data["has_admin_areas"] = HasAdminAreas.NO
        else:
            data["has_admin_areas"] = HasAdminAreas.YES
        return data

    def get_sectors_affected_form_data(self):
        data = {"sectors_affected": None}
        if self.barrier.data["sectors_affected"] is True:
            data["sectors_affected"] = SectorsAffected.YES
        elif self.barrier.data["sectors_affected"] is False:
            data["sectors_affected"] = SectorsAffected.NO
        return data

    def get_selected_sectors(self):
        """Helper to extract selected sectors from barrier data and preload the form."""
        all_sectors = (self.barrier.data.get("all_sectors") is True)
        if all_sectors:
            selected_sectors = "all"
        else:
            sectors = self.barrier.data.get("sectors") or ""
            selected_sectors = ', '.join(sectors)
        return selected_sectors

    def get_about_form(self):
        data = {
            "barrier_title": self.barrier.data.get("barrier_title") or "",
            "product": self.barrier.data.get("product") or "",
            "source": self.barrier.data.get("source"),
            "other_source": self.barrier.data.get("other_source") or "",
            "tags": [t["id"] for t in self.barrier.data.get("tags", ())],
        }
        return data

    def get_summary_form(self):
        data = {
            "problem_description": self.barrier.data.get("problem_description") or "",
            "next_steps_summary": self.barrier.data.get("next_steps_summary") or "",
            "status_summary": self.barrier.data.get("status_summary") or "",
        }
        return data

    def update_session_keys(self):
        """
        Update value of each session key, based on data from self.barrier.data
        """
        self.problem_status_form = self.get_problem_status_form_data()
        self.status_form = self.get_status_form_data()
        self.location_form = self.get_location_form_data()
        self.has_admin_areas = self.get_has_admin_areas_form_data()
        self.selected_admin_areas = ', '.join(self.barrier.data.get("country_admin_areas") or ())
        self.sectors_affected = self.get_sectors_affected_form_data()
        self.selected_about_formsectors = self.get_selected_sectors()
        self.about_form = self.get_about_form()
        self.summary_form = self.get_summary_form()

    def update_context(self, barrier):
        self.barrier = barrier
        self.barrier_id = barrier.id
        self.init_session_keys()
        self.update_session_keys()

    def prepare_payload(self):
        """Combined payload of multiple steps (Status & Location)"""
        payload = {
            "problem_status": self.problem_status_form.get("status"),
            "is_resolved": self.status_form.get("is_resolved"),
            "resolved_date": self.status_form.get("resolved_date"),
            "resolved_status": self.status_form.get("status"),
            "export_country": self.location_form.get("country"),
            "country_admin_areas": self.selected_admin_areas_as_list,
        }

        if payload["resolved_status"] == BarrierStatuses.UNRESOLVED:
            payload["is_resolved"] = False
            payload["resolved_status"] = None
            payload["resolved_date"] = None

        return payload

    def prepare_payload_sectors(self):
        all_sectors = (self.selected_sectors == "all")
        sectors = ()
        sectors_affected = self.sectors_affected.get("sectors_affected")

        if sectors_affected == SectorsAffected.YES:
            if not all_sectors:
                sectors = self.selected_sectors_as_list
        else:
            all_sectors = False

        payload = {
            "sectors_affected": sectors_affected,
            "all_sectors": all_sectors,
            "sectors": sectors,
        }

        return payload

    def prepare_payload_about(self):
        payload = self.about_form
        if not payload["other_source"]:
            payload["other_source"] = None
        return payload

    def prepare_payload_summary(self):
        payload = self.summary_form
        if self.status_form.get("is_resolved"):
            payload["next_steps_summary"] = None
        else:
            payload["status_summary"] = None
            if not payload["next_steps_summary"]:
                payload["next_steps_summary"] = None
        return payload

    def _update_barrier(self, payload):
        return self.client.reports.patch(id=self.barrier_id, **payload)

    def _create_barrier(self, payload):
        return self.client.reports.create(**payload)

    def save(self, payload=None):
        """Create or update a (report) barrier."""
        payload = payload or self.prepare_payload()
        if self.barrier_id:
            barrier = self._update_barrier(payload)
        else:
            barrier = self._create_barrier(payload)
        self.update_context(barrier)

    def submit(self):
        """Create a Barrier out of a Draft Barrier"""
        self.client.reports.submit(barrier_id=self.barrier_id)
        self.flush_session_keys()
