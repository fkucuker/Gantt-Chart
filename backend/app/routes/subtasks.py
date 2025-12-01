# /backend/app/routes/subtasks.py
"""
SubTasks CRUD routes.
"""
from datetime import datetime
from flask import Blueprint, request, jsonify

from ..db import db
from ..models import Activity, Topic, SubTask, SubTaskStatus, UserRole
from ..auth.utils import login_required, role_required, get_current_user

subtasks_bp = Blueprint("subtasks", __name__)


@subtasks_bp.route("/topics/<int:topic_id>/subtasks", methods=["GET"])
@login_required
def get_subtasks(topic_id: int):
    """
    GET /api/topics/:topic_id/subtasks
    Returns: List of subtasks for a topic
    """
    topic = db.session.get(Topic, topic_id)

    if not topic:
        return jsonify({"error": "Konu bulunamadı"}), 404

    subtasks = db.session.query(SubTask).filter_by(topic_id=topic_id).order_by(SubTask.start_date).all()
    return jsonify({
        "subtasks": [st.to_dict(include_assignee=True) for st in subtasks]
    }), 200


@subtasks_bp.route("/topics/<int:topic_id>/subtasks", methods=["POST"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def create_subtask(topic_id: int):
    """
    POST /api/topics/:topic_id/subtasks
    Body: {
        "title": "...",
        "description": "...",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "status": "PLANNED",
        "assignee_id": null,
        "progress_percent": 0
    }
    Returns: Created subtask
    """
    topic = db.session.get(Topic, topic_id)
    current_user = get_current_user()

    if not topic:
        return jsonify({"error": "Konu bulunamadı"}), 404

    # Check permission via activity owner
    activity = db.session.get(Activity, topic.activity_id)
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu konuya alt görev ekleme yetkiniz yok"}), 403

    data = request.get_json()

    # Validation
    required_fields = ["title", "start_date", "end_date"]
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

    # Validate status
    status = SubTaskStatus.PLANNED
    if data.get("status"):
        try:
            status = SubTaskStatus(data["status"])
        except ValueError:
            return jsonify({"error": "Geçersiz durum değeri"}), 400

    # Validate progress
    progress = data.get("progress_percent", 0)
    if not isinstance(progress, int) or progress < 0 or progress > 100:
        return jsonify({"error": "İlerleme yüzdesi 0-100 arasında olmalı"}), 400

    # Check date range warning
    warnings = []
    if start_date < activity.start_date or end_date > activity.end_date:
        warnings.append("Alt görev tarihleri faaliyet tarih aralığının dışında")

    subtask = SubTask(
        topic_id=topic_id,
        title=data["title"],
        description=data.get("description"),
        start_date=start_date,
        end_date=end_date,
        status=status,
        assignee_id=data.get("assignee_id"),
        progress_percent=progress
    )

    db.session.add(subtask)
    db.session.commit()

    response = {"subtask": subtask.to_dict(include_assignee=True)}
    if warnings:
        response["warnings"] = warnings

    return jsonify(response), 201


@subtasks_bp.route("/subtasks/<int:subtask_id>", methods=["PUT"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def update_subtask(subtask_id: int):
    """
    PUT /api/subtasks/:id
    Full update of a subtask
    """
    subtask = db.session.get(SubTask, subtask_id)
    current_user = get_current_user()

    if not subtask:
        return jsonify({"error": "Alt görev bulunamadı"}), 404

    # Check permission via activity owner
    topic = db.session.get(Topic, subtask.topic_id)
    activity = db.session.get(Activity, topic.activity_id)
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu alt görevi güncelleme yetkiniz yok"}), 403

    data = request.get_json()

    if data.get("title"):
        subtask.title = data["title"]

    if "description" in data:
        subtask.description = data.get("description")

    if data.get("start_date"):
        try:
            subtask.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalı"}), 400

    if data.get("end_date"):
        try:
            subtask.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalı"}), 400

    if subtask.start_date > subtask.end_date:
        return jsonify({"error": "Başlangıç tarihi bitiş tarihinden sonra olamaz"}), 400

    if data.get("status"):
        try:
            subtask.status = SubTaskStatus(data["status"])
        except ValueError:
            return jsonify({"error": "Geçersiz durum değeri"}), 400

    if "assignee_id" in data:
        subtask.assignee_id = data.get("assignee_id")

    if "progress_percent" in data:
        progress = data["progress_percent"]
        if not isinstance(progress, int) or progress < 0 or progress > 100:
            return jsonify({"error": "İlerleme yüzdesi 0-100 arasında olmalı"}), 400
        subtask.progress_percent = progress

    db.session.commit()

    return jsonify({"subtask": subtask.to_dict(include_assignee=True)}), 200


@subtasks_bp.route("/subtasks/<int:subtask_id>", methods=["PATCH"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def patch_subtask(subtask_id: int):
    """
    PATCH /api/subtasks/:id
    Partial update - mainly for drag & drop date changes and status updates
    """
    subtask = db.session.get(SubTask, subtask_id)
    current_user = get_current_user()

    if not subtask:
        return jsonify({"error": "Alt görev bulunamadı"}), 404

    # Check permission via activity owner
    topic = db.session.get(Topic, subtask.topic_id)
    activity = db.session.get(Activity, topic.activity_id)
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu alt görevi güncelleme yetkiniz yok"}), 403

    data = request.get_json()

    # Only process provided fields
    if "start_date" in data:
        try:
            subtask.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalı"}), 400

    if "end_date" in data:
        try:
            subtask.end_date = datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Tarih formatı YYYY-MM-DD olmalı"}), 400

    if subtask.start_date > subtask.end_date:
        return jsonify({"error": "Başlangıç tarihi bitiş tarihinden sonra olamaz"}), 400

    if "status" in data:
        try:
            subtask.status = SubTaskStatus(data["status"])
        except ValueError:
            return jsonify({"error": "Geçersiz durum değeri"}), 400

    if "progress_percent" in data:
        progress = data["progress_percent"]
        if not isinstance(progress, int) or progress < 0 or progress > 100:
            return jsonify({"error": "İlerleme yüzdesi 0-100 arasında olmalı"}), 400
        subtask.progress_percent = progress

    db.session.commit()

    return jsonify({"subtask": subtask.to_dict(include_assignee=True)}), 200


@subtasks_bp.route("/subtasks/<int:subtask_id>", methods=["DELETE"])
@login_required
@role_required(UserRole.ADMIN, UserRole.EDITOR)
def delete_subtask(subtask_id: int):
    """
    DELETE /api/subtasks/:id
    Returns: Success message
    """
    subtask = db.session.get(SubTask, subtask_id)
    current_user = get_current_user()

    if not subtask:
        return jsonify({"error": "Alt görev bulunamadı"}), 404

    # Check permission via activity owner
    topic = db.session.get(Topic, subtask.topic_id)
    activity = db.session.get(Activity, topic.activity_id)
    if current_user.role != UserRole.ADMIN and activity.owner_id != current_user.id:
        return jsonify({"error": "Bu alt görevi silme yetkiniz yok"}), 403

    db.session.delete(subtask)
    db.session.commit()

    return jsonify({"message": "Alt görev başarıyla silindi"}), 200

