# /backend/app/routes/topics.py
"""
Topics CRUD routes.
"""
from flask import Blueprint, request, jsonify

from ..db import db
from ..models import Activity, Topic, UserRole
from ..auth.utils import login_required, role_required, get_current_user

topics_bp = Blueprint("topics", __name__)


@topics_bp.route("/activities/<int:activity_id>/topics", methods=["GET"])
@login_required
def get_topics(activity_id: int):
    """
    GET /api/activities/:activity_id/topics
    Returns: List of topics for an activity
    """
    activity = db.session.get(Activity, activity_id)

    if not activity:
        return jsonify({"error": "Faaliyet bulunamadı"}), 404

    topics = db.session.query(Topic).filter_by(activity_id=activity_id).all()
    return jsonify({
        "topics": [t.to_dict(include_subtasks=True) for t in topics]
    }), 200


@topics_bp.route("/activities/<int:activity_id>/topics", methods=["POST"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def create_topic(activity_id: int):
    """
    POST /api/activities/:activity_id/topics
    Body: { "title": "...", "description": "..." }
    Returns: Created topic
    """
    activity = db.session.get(Activity, activity_id)
    current_user = get_current_user()

    if not activity:
        return jsonify({"error": "Faaliyet bulunamadı"}), 404

    # Only owner or admin can add topics
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu faaliyete konu ekleme yetkiniz yok"}), 403

    data = request.get_json()

    if not data.get("title"):
        return jsonify({"error": "Başlık gerekli"}), 400

    topic = Topic(
        activity_id=activity_id,
        title=data["title"],
        description=data.get("description")
    )

    db.session.add(topic)
    db.session.commit()

    return jsonify({"topic": topic.to_dict()}), 201


@topics_bp.route("/topics/<int:topic_id>", methods=["PUT"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def update_topic(topic_id: int):
    """
    PUT /api/topics/:id
    Body: { "title": "...", "description": "..." }
    Returns: Updated topic
    """
    topic = db.session.get(Topic, topic_id)
    current_user = get_current_user()

    if not topic:
        return jsonify({"error": "Konu bulunamadı"}), 404

    # Check permission via activity owner
    activity = db.session.get(Activity, topic.activity_id)
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu konuyu güncelleme yetkiniz yok"}), 403

    data = request.get_json()

    if data.get("title"):
        topic.title = data["title"]

    if "description" in data:
        topic.description = data.get("description")

    db.session.commit()

    return jsonify({"topic": topic.to_dict()}), 200


@topics_bp.route("/topics/<int:topic_id>", methods=["DELETE"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def delete_topic(topic_id: int):
    """
    DELETE /api/topics/:id
    Returns: Success message
    """
    topic = db.session.get(Topic, topic_id)
    current_user = get_current_user()

    if not topic:
        return jsonify({"error": "Konu bulunamadı"}), 404

    # Check permission via activity owner
    activity = db.session.get(Activity, topic.activity_id)
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu konuyu silme yetkiniz yok"}), 403

    db.session.delete(topic)
    db.session.commit()

    return jsonify({"message": "Konu başarıyla silindi"}), 200

