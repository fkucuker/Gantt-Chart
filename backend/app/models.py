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
        # Calculate effective status (OVERDUE if past due and not completed)
        effective_status = self.status
        if self.status != SubTaskStatus.COMPLETED and self.end_date < date.today():
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

