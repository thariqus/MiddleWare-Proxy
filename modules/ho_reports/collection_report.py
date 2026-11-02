from data.ho_reports.collection_report import (
    build_collection_filters,
    format_collection_report
)
from repository.ho_reports.collection_report import fetch_collection_report

def get_collection_report(args):
    filters = build_collection_filters(args)
    rows = fetch_collection_report(filters)
    return {"data": format_collection_report(rows)}