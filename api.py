from flask import Blueprint, jsonify, request
from modules.ho_reports.collection_report import get_collection_report

api = Blueprint("api", __name__)

@api.route("/collection-report")
def collection_report():
    try:
        return jsonify(get_collection_report(request.args))
    except Exception:
        return jsonify({"error": "Failed to fetch collection report"}), 500