from datetime import date, datetime
from decimal import Decimal

def split_filter_values(value):
    if value is None:
        return []

    if isinstance(value, (list, tuple)):
        values = value
    else:
        values = str(value).split("|")
    
    return [str(item).strip() for item in values if str(item).strip()]

def build_collection_filters(args):
    return {
        "from_date": args.get("from_date") or None,
        "to_date": args.get("to_date") or None,
        "customers": split_filter_values(args.get("customer")),
        "sales_orders": split_filter_values(args.get("sales_order")),
        "sales_invoices": split_filter_values(args.get("sales_invoice")),
    }

def _clean(value):
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    return value


def format_collection_report(rows):
    return [{key: _clean(value) for key, value in row.items() for row in rows}]