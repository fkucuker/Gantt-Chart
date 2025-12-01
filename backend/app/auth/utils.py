# /backend/app/auth/utils.py
"""
Authentication utilities - JWT handling and role-based access control.
"""
from datetime import datetime, timedelta
from functools import wraps
from typing import Callable, Optional

import jwt
import bcrypt
from flask import request, jsonify, current_app, g

from ..models import User, UserRole
from ..db import db


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def generate_token(user: User) -> str:
    """Generate a JWT token for a user."""
    expiration_hours = current_app.config.get("JWT_EXPIRATION_HOURS", 24)
    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role.value,
        "exp": datetime.utcnow() + timedelta(hours=expiration_hours),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user() -> Optional[User]:
    """Get the current user from the request context."""
    return getattr(g, "current_user", None)


def login_required(f: Callable) -> Callable:
    """Decorator to require authentication for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Yetkilendirme başlığı gerekli"}), 401

        token = auth_header.split(" ")[1]
        payload = decode_token(token)

        if not payload:
            return jsonify({"error": "Geçersiz veya süresi dolmuş token"}), 401

        user = db.session.get(User, payload["user_id"])
        if not user or not user.is_active:
            return jsonify({"error": "Kullanıcı bulunamadı veya aktif değil"}), 401

        g.current_user = user
        return f(*args, **kwargs)

    return decorated_function


def role_required(*allowed_roles: UserRole) -> Callable:
    """
    Decorator to require specific roles for a route.
    Must be used after @login_required.

    Usage:
        @login_required
        @role_required(UserRole.ADMIN, UserRole.EDITOR)
        def my_route():
            ...
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user = get_current_user()

            if not current_user:
                return jsonify({"error": "Yetkilendirme gerekli"}), 401

            if current_user.role not in allowed_roles:
                return jsonify({"error": "Bu işlem için yetkiniz yok"}), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator

