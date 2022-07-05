from typing import Dict


class FormSessionKeys:
    """
    These (meta) keys are used by ReportFormGroup to help manage form data
    during the "Add a barrier" journey.
    """

    TERM = "TERM"
    STATUS = "STATUS"
    LOCATION = "LOCATION"
    HAS_ADMIN_AREAS = "HAS_ADMIN_AREAS"
    ADMIN_AREAS = "ADMIN_AREAS"
    CAUSED_BY_TRADING_BLOC = "CAUSED_BY_TRADING_BLOC"
    TRADE_DIRECTION = "TRADE_DIRECTION"
    SELECTED_ADMIN_AREAS = "SELECTED_ADMIN_AREAS"
    SECTORS_AFFECTED = "SECTORS_AFFECTED"
    SECTORS = "SECTORS"
    CATEGORIES = "CATEGORIES"
    COMMODITIES = "COMMODITIES"
    ABOUT = "ABOUT"
    SUMMARY = "SUMMARY"


# To simplify the order of the view forms we add a config here
NEW_REPORT_URLS: Dict[str, str] = {
    FormSessionKeys.TERM: "reports:barrier_term",
    FormSessionKeys.STATUS: "reports:barrier_status",
    FormSessionKeys.LOCATION: "reports:barrier_location",
    FormSessionKeys.HAS_ADMIN_AREAS: "reports:barrier_has_admin_areas",
    FormSessionKeys.ADMIN_AREAS: "reports:barrier_admin_areas",
    FormSessionKeys.CAUSED_BY_TRADING_BLOC: "reports:barrier_caused_by_trading_bloc",
    FormSessionKeys.TRADE_DIRECTION: "reports:barrier_trade_direction",
    FormSessionKeys.SELECTED_ADMIN_AREAS: "reports:barrier_selected_admin_areas",
    FormSessionKeys.SECTORS_AFFECTED: "reports:barrier_sectors_affected",
    FormSessionKeys.SECTORS: "reports:barrier_sectors",
    FormSessionKeys.CATEGORIES: "reports:barrier_categories",
    FormSessionKeys.COMMODITIES: "reports:barrier_commodities",
    FormSessionKeys.ABOUT: "reports:barrier_about",
    FormSessionKeys.SUMMARY: "reports:barrier_summary",
}


NEW_REPORT_ORDER_CONFIG = {FormSessionKeys.ABOUT: {"next": ""}}
