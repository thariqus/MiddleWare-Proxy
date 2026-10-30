from flask import Blueprint, jsonify, request
from service.ho_reports.item_report import get_items

api = Blueprint("api", __name__)

@api.route("/items")
def items():
    limit = request.args.get("limit", 100, type=int)
    return jsonify(get_items(limit))