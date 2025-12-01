# /backend/app/routes/notifications.py
"""
Notifications API routes - FAZ-2 feature.
"""
from flask import Blueprint, request, jsonify

from ..db import db
from ..models import Notification
from ..auth.utils import login_required, get_current_user
from ..services.notification_service import notification_service

notifications_bp = Blueprint("notifications", __name__)


@notifications_bp.route("/notifications", methods=["GET"])
@login_required
def get_notifications():
    """
    GET /api/notifications
    Query params:
        - unread_only: bool (default False)
        - limit: int (default 50, max 100)
    Returns: List of notifications for the current user
    """
    current_user = get_current_user()
    
    unread_only = request.args.get("unread_only", "false").lower() == "true"
    limit = min(int(request.args.get("limit", 50)), 100)
    
    notifications = notification_service.get_user_notifications(
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit
    )
    
    unread_count = notification_service.get_unread_count(current_user.id)
    
    return jsonify({
        "notifications": [n.to_dict(include_relations=True) for n in notifications],
        "unread_count": unread_count
    }), 200


@notifications_bp.route("/notifications/unread-count", methods=["GET"])
@login_required
def get_unread_count():
    """
    GET /api/notifications/unread-count
    Returns: Count of unread notifications
    """
    current_user = get_current_user()
    count = notification_service.get_unread_count(current_user.id)
    
    return jsonify({"unread_count": count}), 200


@notifications_bp.route("/notifications/<int:notification_id>", methods=["PATCH"])
@login_required
def mark_notification_read(notification_id: int):
    """
    PATCH /api/notifications/:id
    Body: { "is_read": true }
    Returns: Updated notification
    """
    current_user = get_current_user()
    data = request.get_json()
    
    if data.get("is_read") is not True:
        return jsonify({"error": "Sadece is_read: true değeri kabul edilir"}), 400
    
    notification = notification_service.mark_as_read(notification_id, current_user.id)
    
    if not notification:
        return jsonify({"error": "Bildirim bulunamadı veya yetkiniz yok"}), 404
    
    return jsonify({"notification": notification.to_dict(include_relations=True)}), 200


@notifications_bp.route("/notifications/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    """
    POST /api/notifications/mark-all-read
    Returns: Number of notifications marked as read
    """
    current_user = get_current_user()
    count = notification_service.mark_all_as_read(current_user.id)
    
    return jsonify({
        "message": f"{count} bildirim okundu olarak işaretlendi",
        "marked_count": count
    }), 200


@notifications_bp.route("/notifications/<int:notification_id>", methods=["DELETE"])
@login_required
def delete_notification(notification_id: int):
    """
    DELETE /api/notifications/:id
    Returns: Success message
    """
    current_user = get_current_user()
    
    if notification_service.delete_notification(notification_id, current_user.id):
        return jsonify({"message": "Bildirim silindi"}), 200
    
    return jsonify({"error": "Bildirim bulunamadı veya yetkiniz yok"}), 404

