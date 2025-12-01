# /backend/app/auth/routes.py
"""
Authentication routes - login, me, logout.
"""
from flask import Blueprint, request, jsonify

from ..db import db
from ..models import User
from .utils import verify_password, generate_token, login_required, get_current_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { "email": "...", "password": "..." }
    Returns: { "token": "...", "user": {...} }
    """
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email ve şifre gerekli"}), 400

    user = db.session.query(User).filter_by(email=data["email"]).first()

    if not user or not verify_password(data["password"], user.password_hash):
        return jsonify({"error": "Geçersiz email veya şifre"}), 401

    if not user.is_active:
        return jsonify({"error": "Hesabınız aktif değil"}), 403

    token = generate_token(user)

    return jsonify({
        "token": token,
        "user": user.to_dict(include_email=True)
    }), 200


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """
    GET /api/auth/me
    Returns: Current user information
    """
    current_user = get_current_user()
    return jsonify({"user": current_user.to_dict(include_email=True)}), 200


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    POST /api/auth/logout
    Returns: Success message (token invalidation is client-side)
    """
    # JWT tokens are stateless, so logout is handled client-side
    # by removing the token from storage
    return jsonify({"message": "Başarıyla çıkış yapıldı"}), 200

