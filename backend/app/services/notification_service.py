# /backend/app/services/notification_service.py
"""
Notification Service - FAZ-2 feature
Handles creation and management of user notifications.
"""
from typing import Optional, List
from datetime import datetime

from ..db import db
from ..models import Notification, User, Activity, SubTask, NotificationType


class NotificationService:
    """Service class for notification operations."""

    @staticmethod
    def create_notification(
        notification_type: str,
        message: str,
        target_user_id: int,
        created_by_id: Optional[int] = None,
        activity_id: Optional[int] = None,
        subtask_id: Optional[int] = None
    ) -> Notification:
        """
        Create a new notification.
        
        Args:
            notification_type: Type of notification (from NotificationType enum)
            message: Short message describing the notification
            target_user_id: User who will receive the notification
            created_by_id: User who triggered the notification (optional)
            activity_id: Related activity ID (optional)
            subtask_id: Related subtask ID (optional)
        
        Returns:
            Created Notification object
        """
        notification = Notification(
            type=notification_type,
            message=message,
            target_user_id=target_user_id,
            created_by_id=created_by_id,
            activity_id=activity_id,
            subtask_id=subtask_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @staticmethod
    def get_user_notifications(
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """
        Get notifications for a user.
        
        Args:
            user_id: Target user ID
            unread_only: If True, only return unread notifications
            limit: Maximum number of notifications to return
        
        Returns:
            List of Notification objects
        """
        query = db.session.query(Notification).filter_by(target_user_id=user_id)
        
        if unread_only:
            query = query.filter_by(is_read=False)
        
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread notifications for a user."""
        return db.session.query(Notification).filter_by(
            target_user_id=user_id,
            is_read=False
        ).count()

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> Optional[Notification]:
        """
        Mark a notification as read.
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for permission check)
        
        Returns:
            Updated Notification or None if not found/unauthorized
        """
        notification = db.session.get(Notification, notification_id)
        
        if not notification or notification.target_user_id != user_id:
            return None
        
        notification.is_read = True
        db.session.commit()
        return notification

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """
        Mark all notifications as read for a user.
        
        Args:
            user_id: Target user ID
        
        Returns:
            Number of notifications marked as read
        """
        result = db.session.query(Notification).filter_by(
            target_user_id=user_id,
            is_read=False
        ).update({"is_read": True})
        db.session.commit()
        return result

    @staticmethod
    def delete_notification(notification_id: int, user_id: int) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for permission check)
        
        Returns:
            True if deleted, False otherwise
        """
        notification = db.session.get(Notification, notification_id)
        
        if not notification or notification.target_user_id != user_id:
            return False
        
        db.session.delete(notification)
        db.session.commit()
        return True

    # Convenience methods for common notification types
    @staticmethod
    def notify_task_assigned(
        subtask: SubTask,
        assignee_id: int,
        assigned_by_id: int
    ) -> Optional[Notification]:
        """Notify user when a task is assigned to them."""
        if assignee_id == assigned_by_id:
            return None  # Don't notify if assigning to self
        
        return NotificationService.create_notification(
            notification_type=NotificationType.TASK_ASSIGNED.value,
            message=f'"{subtask.title}" görevi size atandı.',
            target_user_id=assignee_id,
            created_by_id=assigned_by_id,
            subtask_id=subtask.id,
            activity_id=subtask.topic.activity_id if subtask.topic else None
        )

    @staticmethod
    def notify_date_changed(
        subtask: SubTask,
        target_user_id: int,
        changed_by_id: int,
        old_start: str,
        old_end: str
    ) -> Optional[Notification]:
        """Notify user when task dates are changed (e.g., via drag & drop)."""
        if target_user_id == changed_by_id:
            return None  # Don't notify if changing own task
        
        return NotificationService.create_notification(
            notification_type=NotificationType.DATE_CHANGED.value,
            message=f'"{subtask.title}" görevinin tarihleri güncellendi: {subtask.start_date} - {subtask.end_date}',
            target_user_id=target_user_id,
            created_by_id=changed_by_id,
            subtask_id=subtask.id,
            activity_id=subtask.topic.activity_id if subtask.topic else None
        )

    @staticmethod
    def notify_status_changed(
        subtask: SubTask,
        target_user_id: int,
        changed_by_id: int,
        new_status: str
    ) -> Optional[Notification]:
        """Notify user when task status changes."""
        if target_user_id == changed_by_id:
            return None
        
        status_labels = {
            "PLANNED": "Planlandı",
            "IN_PROGRESS": "Devam Ediyor",
            "COMPLETED": "Tamamlandı",
            "OVERDUE": "Gecikmiş"
        }
        status_label = status_labels.get(new_status, new_status)
        
        return NotificationService.create_notification(
            notification_type=NotificationType.STATUS_CHANGED.value,
            message=f'"{subtask.title}" görevinin durumu "{status_label}" olarak değiştirildi.',
            target_user_id=target_user_id,
            created_by_id=changed_by_id,
            subtask_id=subtask.id,
            activity_id=subtask.topic.activity_id if subtask.topic else None
        )


# Singleton instance for convenience
notification_service = NotificationService()

