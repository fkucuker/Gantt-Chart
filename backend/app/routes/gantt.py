# /backend/app/routes/gantt.py
"""
Gantt chart data endpoint.
"""
from datetime import date
from flask import Blueprint, jsonify

from ..db import db
from ..models import Activity, Topic, SubTask
from ..auth.utils import login_required
from ..services.gantt_service import calculate_scale

gantt_bp = Blueprint("gantt", __name__)


@gantt_bp.route("/activities/<int:activity_id>/gantt", methods=["GET"])
@login_required
def get_gantt_data(activity_id: int):
    """
    GET /api/activities/:id/gantt
    Returns: Full gantt chart data including activity, topics, subtasks, scale
    """
    activity = db.session.get(Activity, activity_id)

    if not activity:
        return jsonify({"error": "Faaliyet bulunamadı"}), 404

    # Get all topics for this activity
    topics = db.session.query(Topic).filter_by(activity_id=activity_id).all()

    # Get all subtasks for all topics
    topic_ids = [t.id for t in topics]
    subtasks = []
    if topic_ids:
        subtasks = db.session.query(SubTask).filter(
            SubTask.topic_id.in_(topic_ids)
        ).order_by(SubTask.start_date).all()

    # Calculate appropriate scale
    scale = calculate_scale(activity.start_date, activity.end_date)

    return jsonify({
        "activity": activity.to_dict(include_owner=True),
        "topics": [t.to_dict() for t in topics],
        "subtasks": [st.to_dict(include_assignee=True) for st in subtasks],
        "scale": scale,
        "today": date.today().isoformat()
    }), 200

