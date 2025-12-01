# /backend/app/models.py
"""
Database Models - SQLAlchemy 2.x with type annotations
"""
from datetime import datetime, date
from enum import Enum as PyEnum
from typing import Optional, List

from sqlalchemy import String, Text, Integer, Boolean, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import db


class UserRole(PyEnum):
    """User role enumeration - values match database enum."""
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class SubTaskStatus(PyEnum):
    """SubTask status enumeration - values match database enum."""
    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class NotificationType(PyEnum):
    """Notification type enumeration."""
    TASK_CREATED = "TASK_CREATED"
    TASK_UPDATED = "TASK_UPDATED"
    TASK_DELETED = "TASK_DELETED"
    TASK_ASSIGNED = "TASK_ASSIGNED"
    TASK_COMPLETED = "TASK_COMPLETED"
    TASK_OVERDUE = "TASK_OVERDUE"
    DATE_CHANGED = "DATE_CHANGED"
    STATUS_CHANGED = "STATUS_CHANGED"


def enum_values_callable(enum_class):
    """Return enum values instead of names for database storage."""
    return [e.value for e in enum_class]


class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=enum_values_callable, create_constraint=False),
        default=UserRole.VIEWER,
        nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    owned_activities: Mapped[List["Activity"]] = relationship(
        "Activity", back_populates="owner", foreign_keys="Activity.owner_id"
    )
    assigned_subtasks: Mapped[List["SubTask"]] = relationship(
        "SubTask", back_populates="assignee", foreign_keys="SubTask.assignee_id"
    )
    received_notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="target_user", foreign_keys="Notification.target_user_id"
    )
    created_notifications: Mapped[List["Notification"]] = relationship(
        "Notification", back_populates="created_by", foreign_keys="Notification.created_by_id"
    )

    def to_dict(self, include_email: bool = False) -> dict:
        """Convert user to dictionary representation."""
        data = {
            "id": self.id,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_email:
            data["email"] = self.email
        return data


class Activity(db.Model):
    """Activity model - top level planning entity."""
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    owner_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="owned_activities")
    topics: Mapped[List["Topic"]] = relationship(
        "Topic", back_populates="activity", cascade="all, delete-orphan"
    )

    def to_dict(self, include_owner: bool = False) -> dict:
        """Convert activity to dictionary representation."""
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_owner and self.owner:
            data["owner"] = self.owner.to_dict()
        return data


class Topic(db.Model):
    """Topic model - groups subtasks within an activity."""
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    activity_id: Mapped[int] = mapped_column(Integer, ForeignKey("activities.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    activity: Mapped["Activity"] = relationship("Activity", back_populates="topics")
    subtasks: Mapped[List["SubTask"]] = relationship(
        "SubTask", back_populates="topic", cascade="all, delete-orphan"
    )

    def to_dict(self, include_subtasks: bool = False) -> dict:
        """Convert topic to dictionary representation."""
        data = {
            "id": self.id,
            "activity_id": self.activity_id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_subtasks:
            data["subtasks"] = [st.to_dict() for st in self.subtasks]
        return data


class SubTask(db.Model):
    """SubTask model - individual tasks with dates and status."""
    __tablename__ = "subtasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[SubTaskStatus] = mapped_column(
        Enum(SubTaskStatus, name="subtask_status", values_callable=enum_values_callable, create_constraint=False),
        default=SubTaskStatus.PLANNED,
        nullable=False
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    topic: Mapped["Topic"] = relationship("Topic", back_populates="subtasks")
    assignee: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_subtasks")

    def to_dict(self, include_assignee: bool = False) -> dict:
        """Convert subtask to dictionary representation."""
        # Calculate effective status based on progress and completion
        effective_status = self.status
        
        # 1. Auto-complete: If progress is 100% OR status is COMPLETED → show as COMPLETED
        if self.progress_percent == 100 or self.status == SubTaskStatus.COMPLETED:
            effective_status = SubTaskStatus.COMPLETED
        
        # 2. Auto-overdue: If end_date passed AND not fully completed → show as OVERDUE
        # Task is fully completed only if BOTH progress=100% AND status=COMPLETED
        elif self.end_date < date.today():
            effective_status = SubTaskStatus.OVERDUE

        data = {
            "id": self.id,
            "topic_id": self.topic_id,
            "title": self.title,
            "description": self.description,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": effective_status.value,
            "assignee_id": self.assignee_id,
            "progress_percent": self.progress_percent,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_assignee and self.assignee:
            data["assignee"] = self.assignee.to_dict()
        return data


class Notification(db.Model):
    """Notification model - FAZ-2 feature for user notifications."""
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    message: Mapped[str] = mapped_column(String(500), nullable=False)
    activity_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("activities.id", ondelete="SET NULL"), nullable=True
    )
    subtask_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("subtasks.id", ondelete="SET NULL"), nullable=True
    )
    target_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    created_by_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=True
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    target_user: Mapped["User"] = relationship(
        "User", back_populates="received_notifications", foreign_keys=[target_user_id]
    )
    created_by: Mapped[Optional["User"]] = relationship(
        "User", back_populates="created_notifications", foreign_keys=[created_by_id]
    )
    activity: Mapped[Optional["Activity"]] = relationship("Activity")
    subtask: Mapped[Optional["SubTask"]] = relationship("SubTask")

    def to_dict(self, include_relations: bool = False) -> dict:
        """Convert notification to dictionary representation."""
        data = {
            "id": self.id,
            "type": self.type,
            "message": self.message,
            "activity_id": self.activity_id,
            "subtask_id": self.subtask_id,
            "target_user_id": self.target_user_id,
            "created_by_id": self.created_by_id,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }
        if include_relations:
            if self.created_by:
                data["created_by"] = self.created_by.to_dict()
            if self.activity:
                data["activity"] = {"id": self.activity.id, "name": self.activity.name}
            if self.subtask:
                data["subtask"] = {"id": self.subtask.id, "title": self.subtask.title}
        return data

