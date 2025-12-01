# /backend/app/routes/activities.py
"""
Activities CRUD routes.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from ..db import db
from ..models import Activity, UserRole
from ..auth.utils import login_required, role_required, get_current_user

activities_bp = Blueprint("activities", __name__)


@activities_bp.route("", methods=["GET"])
@login_required
def get_activities():
    """
    GET /api/activities
    Query params: ?owner_id=X (optional filter)
    Returns: List of all activities
    """
    query = db.session.query(Activity)

    # Optional filter by owner
    owner_id = request.args.get("owner_id", type=int)
    if owner_id:
        query = query.filter_by(owner_id=owner_id)

    activities = query.order_by(Activity.start_date.desc()).all()
    return jsonify({
        "activities": [a.to_dict(include_owner=True) for a in activities]
    }), 200


@activities_bp.route("", methods=["POST"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def create_activity():
    """
    POST /api/activities
    Body: { "name": "...", "description": "...", "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" }
    Returns: Created activity
    """
    data = request.get_json()
    current_user = get_current_user()

    # Validation
    required_fields = ["name", "start_date", "end_date"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} alanı gerekli"}), 400

    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalı"}), 400

    if start_date > end_date:
        return jsonify({"error": "Başlangıç tarihi bitiş tarihinden sonra olamaz"}), 400

    activity = Activity(
        name=data["name"],
        description=data.get("description"),
        start_date=start_date,
        end_date=end_date,
        owner_id=current_user.id
    )

    db.session.add(activity)
    db.session.commit()

    return jsonify({"activity": activity.to_dict(include_owner=True)}), 201


@activities_bp.route("/<int:activity_id>", methods=["GET"])
@login_required
def get_activity(activity_id: int):
    """
    GET /api/activities/:id
    Returns: Single activity details
    """
    activity = db.session.get(Activity, activity_id)

    if not activity:
        return jsonify({"error": "Faaliyet bulunamadı"}), 404

    return jsonify({"activity": activity.to_dict(include_owner=True)}), 200


@activities_bp.route("/<int:activity_id>", methods=["PUT"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def update_activity(activity_id: int):
    """
    PUT /api/activities/:id
    Body: { "name": "...", "description": "...", "start_date": "...", "end_date": "..." }
    Returns: Updated activity
    """
    activity = db.session.get(Activity, activity_id)
    current_user = get_current_user()

    if not activity:
        return jsonify({"error": "Faaliyet bulunamadı"}), 404

    # Only owner or admin can update
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu faaliyeti güncelleme yetkiniz yok"}), 403

    data = request.get_json()

    if data.get("name"):
        activity.name = data["name"]

    if "description" in data:
        activity.description = data.get("description")

    if data.get("start_date"):
        try:
            activity.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalı"}), 400

    if data.get("end_date"):
        try:
            activity.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalı"}), 400

    if activity.start_date > activity.end_date:
        return jsonify({"error": "Başlangıç tarihi bitiş tarihinden sonra olamaz"}), 400

    db.session.commit()

    return jsonify({"activity": activity.to_dict(include_owner=True)}), 200


@activities_bp.route("/<int:activity_id>", methods=["DELETE"])
@login_required
@role_required(UserRole.ADMIN)
def delete_activity(activity_id: int):
    """
    DELETE /api/activities/:id
    Returns: Success message (only admin can delete)
    """
    activity = db.session.get(Activity, activity_id)

    if not activity:
        return jsonify({"error": "Faaliyet bulunamadı"}), 404

    db.session.delete(activity)
    db.session.commit()

    return jsonify({"message": "Faaliyet başarıyla silindi"}), 200

