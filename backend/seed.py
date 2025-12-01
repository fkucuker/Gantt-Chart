# /backend/seed.py
"""
Database seed script - creates initial data for development.
"""
from datetime import date, timedelta, datetime

from app import create_app
from app.db import db
from app.models import User, Activity, Topic, SubTask, UserRole, SubTaskStatus
from app.auth.utils import hash_password


def seed_database():
    """Seed the database with initial development data."""
    app = create_app()

    with app.app_context():
        # Clear existing data
        db.session.query(SubTask).delete()
        db.session.query(Topic).delete()
        db.session.query(Activity).delete()
        db.session.query(User).delete()
        db.session.commit()

        # Create users
        admin = User(
            email="admin@gantt.local",
            password_hash=hash_password("admin123"),
            full_name="Sistem Yöneticisi",
            role=UserRole.ADMIN,
            is_active=True
        )
        editor = User(
            email="editor@gantt.local",
            password_hash=hash_password("editor123"),
            full_name="Proje Editörü",
            role=UserRole.EDITOR,
            is_active=True
        )
        viewer = User(
            email="viewer@gantt.local",
            password_hash=hash_password("viewer123"),
            full_name="İzleyici Kullanıcı",
            role=UserRole.VIEWER,
            is_active=True
        )

        db.session.add_all([admin, editor, viewer])
        db.session.commit()

        print(f"✓ Kullanıcılar oluşturuldu: admin, editor, viewer")

        # Create sample activity
        today = date.today()
        activity = Activity(
            name="Web Uygulaması Geliştirme",
            description="Gantt Chart tabanlı proje yönetim uygulaması geliştirme projesi",
            start_date=today - timedelta(days=10),
            end_date=today + timedelta(days=50),
            owner_id=admin.id
        )
        db.session.add(activity)
        db.session.commit()

        print(f"✓ Örnek faaliyet oluşturuldu: {activity.name}")

        # Create topics
        topic1 = Topic(
            activity_id=activity.id,
            title="Backend Geliştirme",
            description="Flask API ve veritabanı işlemleri"
        )
        topic2 = Topic(
            activity_id=activity.id,
            title="Frontend Geliştirme",
            description="Vue 3 + TypeScript arayüz geliştirme"
        )
        topic3 = Topic(
            activity_id=activity.id,
            title="DevOps & Deployment",
            description="Docker, CI/CD ve deployment işlemleri"
        )

        db.session.add_all([topic1, topic2, topic3])
        db.session.commit()

        print(f"✓ Konular oluşturuldu: Backend, Frontend, DevOps")

        # Create subtasks
        subtasks = [
            # Backend subtasks
            SubTask(
                topic_id=topic1.id,
                title="Veritabanı Şeması Tasarımı",
                description="PostgreSQL şema tasarımı ve migration'lar",
                start_date=today - timedelta(days=10),
                end_date=today - timedelta(days=5),
                status=SubTaskStatus.COMPLETED,
                assignee_id=admin.id,
                progress_percent=100
            ),
            SubTask(
                topic_id=topic1.id,
                title="API Endpoint'leri",
                description="REST API endpoint'lerinin geliştirilmesi",
                start_date=today - timedelta(days=5),
                end_date=today + timedelta(days=5),
                status=SubTaskStatus.IN_PROGRESS,
                assignee_id=editor.id,
                progress_percent=60
            ),
            SubTask(
                topic_id=topic1.id,
                title="Kimlik Doğrulama",
                description="JWT tabanlı authentication sistemi",
                start_date=today + timedelta(days=3),
                end_date=today + timedelta(days=10),
                status=SubTaskStatus.PLANNED,
                assignee_id=admin.id,
                progress_percent=0
            ),
            # Frontend subtasks
            SubTask(
                topic_id=topic2.id,
                title="Proje Kurulumu",
                description="Vue 3 + Vite + TypeScript proje yapısı",
                start_date=today - timedelta(days=8),
                end_date=today - timedelta(days=6),
                status=SubTaskStatus.COMPLETED,
                assignee_id=editor.id,
                progress_percent=100
            ),
            SubTask(
                topic_id=topic2.id,
                title="Gantt Bileşenleri",
                description="Gantt chart UI bileşenlerinin geliştirilmesi",
                start_date=today - timedelta(days=3),
                end_date=today + timedelta(days=15),
                status=SubTaskStatus.IN_PROGRESS,
                assignee_id=editor.id,
                progress_percent=35
            ),
            SubTask(
                topic_id=topic2.id,
                title="Dark/Light Tema",
                description="Tema değiştirme ve stil sistemi",
                start_date=today + timedelta(days=10),
                end_date=today + timedelta(days=18),
                status=SubTaskStatus.PLANNED,
                assignee_id=editor.id,
                progress_percent=0
            ),
            # DevOps subtasks
            SubTask(
                topic_id=topic3.id,
                title="Docker Yapılandırması",
                description="Dockerfile ve docker-compose hazırlanması",
                start_date=today + timedelta(days=15),
                end_date=today + timedelta(days=22),
                status=SubTaskStatus.PLANNED,
                assignee_id=admin.id,
                progress_percent=0
            ),
            SubTask(
                topic_id=topic3.id,
                title="Production Deployment",
                description="Canlıya alma ve son testler",
                start_date=today + timedelta(days=40),
                end_date=today + timedelta(days=50),
                status=SubTaskStatus.PLANNED,
                assignee_id=admin.id,
                progress_percent=0
            ),
        ]

        db.session.add_all(subtasks)
        db.session.commit()

        print(f"✓ {len(subtasks)} alt görev oluşturuldu")
        print("\n" + "="*50)
        print("Seed işlemi tamamlandı!")
        print("="*50)
        print("\nGiriş bilgileri:")
        print("  Admin:  admin@gantt.local  / admin123")
        print("  Editor: editor@gantt.local / editor123")
        print("  Viewer: viewer@gantt.local / viewer123")


if __name__ == "__main__":
    seed_database()

