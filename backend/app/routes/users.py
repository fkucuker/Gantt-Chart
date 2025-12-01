# /backend/app/routes/users.py
"""
User management routes - CRUD operations with role-based access control.

Admin:
- Can create, update, delete any user
- Can change user passwords without knowing old password

Other users (Editor, Viewer):
- Can only update their own profile
- Can only delete their own account
- Must provide old password to change their password
"""
from flask import Blueprint, request, jsonify

from ..db import db
from ..models import User, UserRole
from ..auth.utils import (
    login_required,
    role_required,
    get_current_user,
    hash_password,
    verify_password
)

users_bp = Blueprint("users", __name__)


@users_bp.route("/users", methods=["GET"])
@login_required
def get_users():
    """
    GET /api/users
    Returns: List of all users (admin only gets full list, others get minimal info)
    """
    current_user = get_current_user()
    
    # Admin gets full user list with all details
    if current_user.role == UserRole.ADMIN:
        users = db.session.query(User).order_by(User.created_at.desc()).all()
        return jsonify({
            "users": [user.to_dict(include_email=True) for user in users]
        }), 200
    
    # Non-admins only get basic user info (for assignee dropdowns etc.)
    users = db.session.query(User).filter_by(is_active=True).all()
    return jsonify({
        "users": [{"id": u.id, "full_name": u.full_name, "role": u.role.value} for u in users]
    }), 200


@users_bp.route("/users/<int:user_id>", methods=["GET"])
@login_required
def get_user(user_id: int):
    """
    GET /api/users/:id
    Returns: User details
    """
    current_user = get_current_user()
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    
    # Admin can view any user, others can only view themselves
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        return jsonify({"error": "Bu kullanıcıyı görüntüleme yetkiniz yok"}), 403
    
    return jsonify({"user": user.to_dict(include_email=True)}), 200


@users_bp.route("/users", methods=["POST"])
@login_required
@role_required(UserRole.ADMIN)
def create_user():
    """
    POST /api/users
    Body: { "email": "...", "password": "...", "full_name": "...", "role": "..." }
    Returns: Created user (Admin only)
    """
    data = request.get_json()
    
    # Validate required fields
    if not data.get("email"):
        return jsonify({"error": "Email gerekli"}), 400
    if not data.get("password"):
        return jsonify({"error": "Şifre gerekli"}), 400
    if not data.get("full_name"):
        return jsonify({"error": "Ad soyad gerekli"}), 400
    
    # Check if email already exists
    existing_user = db.session.query(User).filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"error": "Bu email adresi zaten kullanılıyor"}), 400
    
    # Validate role if provided
    role = UserRole.VIEWER  # Default role
    if data.get("role"):
        try:
            role = UserRole(data["role"])
        except ValueError:
            return jsonify({"error": f"Geçersiz rol. Geçerli roller: {[r.value for r in UserRole]}"}), 400
    
    # Validate password length
    if len(data["password"]) < 6:
        return jsonify({"error": "Şifre en az 6 karakter olmalıdır"}), 400
    
    # Create user
    user = User(
        email=data["email"],
        password_hash=hash_password(data["password"]),
        full_name=data["full_name"],
        role=role,
        is_active=data.get("is_active", True)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        "message": "Kullanıcı başarıyla oluşturuldu",
        "user": user.to_dict(include_email=True)
    }), 201


@users_bp.route("/users/<int:user_id>", methods=["PUT"])
@login_required
def update_user(user_id: int):
    """
    PUT /api/users/:id
    Body: { "email": "...", "full_name": "...", "role": "...", "is_active": true }
    
    Admin: Can update any user's info including role and is_active
    Others: Can only update their own full_name and email
    """
    current_user = get_current_user()
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    
    # Check permissions
    is_admin = current_user.role == UserRole.ADMIN
    is_self = current_user.id == user_id
    
    if not is_admin and not is_self:
        return jsonify({"error": "Bu kullanıcıyı düzenleme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    # Update email (both admin and self can update)
    if "email" in data and data["email"] != user.email:
        # Check if new email is already in use
        existing = db.session.query(User).filter_by(email=data["email"]).first()
        if existing and existing.id != user_id:
            return jsonify({"error": "Bu email adresi zaten kullanılıyor"}), 400
        user.email = data["email"]
    
    # Update full_name (both admin and self can update)
    if "full_name" in data:
        if not data["full_name"]:
            return jsonify({"error": "Ad soyad boş olamaz"}), 400
        user.full_name = data["full_name"]
    
    # Admin-only fields
    if is_admin:
        # Update role
        if "role" in data:
            try:
                new_role = UserRole(data["role"])
                # Prevent admin from changing their own role (safety)
                if is_self and new_role != UserRole.ADMIN:
                    return jsonify({"error": "Kendi admin rolünüzü değiştiremezsiniz"}), 400
                user.role = new_role
            except ValueError:
                return jsonify({"error": f"Geçersiz rol. Geçerli roller: {[r.value for r in UserRole]}"}), 400
        
        # Update is_active
        if "is_active" in data:
            # Prevent admin from deactivating themselves
            if is_self and not data["is_active"]:
                return jsonify({"error": "Kendi hesabınızı devre dışı bırakamazsınız"}), 400
            user.is_active = data["is_active"]
    else:
        # Non-admin trying to change restricted fields
        if "role" in data or "is_active" in data:
            return jsonify({"error": "Rol ve aktiflik durumunu sadece admin değiştirebilir"}), 403
    
    db.session.commit()
    
    return jsonify({
        "message": "Kullanıcı başarıyla güncellendi",
        "user": user.to_dict(include_email=True)
    }), 200


@users_bp.route("/users/<int:user_id>/password", methods=["PUT"])
@login_required
def change_password(user_id: int):
    """
    PUT /api/users/:id/password
    
    Admin: Body: { "new_password": "..." }
           - Can change any user's password without old password
    
    Others: Body: { "old_password": "...", "new_password": "..." }
            - Can only change their own password
            - Must provide correct old password
    """
    current_user = get_current_user()
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    
    is_admin = current_user.role == UserRole.ADMIN
    is_self = current_user.id == user_id
    
    # Non-admins can only change their own password
    if not is_admin and not is_self:
        return jsonify({"error": "Bu kullanıcının şifresini değiştirme yetkiniz yok"}), 403
    
    data = request.get_json()
    
    # Validate new password
    if not data.get("new_password"):
        return jsonify({"error": "Yeni şifre gerekli"}), 400
    
    if len(data["new_password"]) < 6:
        return jsonify({"error": "Yeni şifre en az 6 karakter olmalıdır"}), 400
    
    # Non-admin users must provide old password
    if not is_admin:
        if not data.get("old_password"):
            return jsonify({"error": "Mevcut şifre gerekli"}), 400
        
        if not verify_password(data["old_password"], user.password_hash):
            return jsonify({"error": "Mevcut şifre hatalı"}), 400
    
    # Update password
    user.password_hash = hash_password(data["new_password"])
    db.session.commit()
    
    return jsonify({"message": "Şifre başarıyla değiştirildi"}), 200


@users_bp.route("/users/<int:user_id>", methods=["DELETE"])
@login_required
def delete_user(user_id: int):
    """
    DELETE /api/users/:id
    
    Admin: Can delete any user (except themselves)
    Others: Can only delete their own account
    """
    current_user = get_current_user()
    user = db.session.get(User, user_id)
    
    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404
    
    is_admin = current_user.role == UserRole.ADMIN
    is_self = current_user.id == user_id
    
    # Check permissions
    if not is_admin and not is_self:
        return jsonify({"error": "Bu kullanıcıyı silme yetkiniz yok"}), 403
    
    # Admin cannot delete themselves
    if is_admin and is_self:
        return jsonify({"error": "Kendi hesabınızı silemezsiniz"}), 400
    
    # Check if user has activities
    if user.owned_activities:
        # Option 1: Prevent deletion
        return jsonify({
            "error": "Bu kullanıcının sahip olduğu faaliyetler var. Önce faaliyetleri başka bir kullanıcıya devredin veya silin."
        }), 400
        # Option 2: Soft delete (deactivate instead)
        # user.is_active = False
        # db.session.commit()
        # return jsonify({"message": "Kullanıcı devre dışı bırakıldı (faaliyetleri olduğu için tam silinemedi)"}), 200
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "Kullanıcı başarıyla silindi"}), 200


@users_bp.route("/users/me", methods=["PUT"])
@login_required
def update_current_user():
    """
    PUT /api/users/me
    Body: { "email": "...", "full_name": "..." }
    
    Convenience endpoint for updating current user's profile.
    Same as PUT /api/users/:id for self.
    """
    current_user = get_current_user()
    return update_user(current_user.id)


@users_bp.route("/users/me/password", methods=["PUT"])
@login_required
def change_current_user_password():
    """
    PUT /api/users/me/password
    Body: { "old_password": "...", "new_password": "..." }
    
    Convenience endpoint for changing current user's password.
    Same as PUT /api/users/:id/password for self.
    """
    current_user = get_current_user()
    return change_password(current_user.id)

