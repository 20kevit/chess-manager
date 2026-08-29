"""
User Management Service.

Handles user and role management for system administrators.
"""
from typing import List, Dict, Optional

from app.extensions import db

from infrastructure.models.user import UserModel, UserRoleModel
from infrastructure.repositories.user import UserRepository


class UserManagementService:
    """Service for managing users and their roles."""

    VALID_ROLES = ['player', 'organizer', 'arbiter']

    @staticmethod
    def get_all_users() -> List[UserModel]:
        """Legacy: Get all users ordered by email."""
        return UserModel.query.order_by(UserModel.email).all()

    @staticmethod
    def get_users_paginated(page: int, per_page: int, search: str = '', role_filter: str = '') -> dict:
        """Get paginated, filtered, and searched users."""
        query = UserModel.query

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    UserModel.email.ilike(search_term)
                )
            )

        if role_filter:
            if role_filter == 'admin':
                query = query.filter(UserModel.is_admin == True)
            else:
                query = query.join(UserRoleModel).filter(UserRoleModel.role == role_filter)

        query = query.order_by(UserModel.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'users': pagination.items,
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_page': page - 1 if pagination.has_prev else None,
            'next_page': page + 1 if pagination.has_next else None,
        }

    @staticmethod
    def get_user_detail(user_id: int) -> Optional[UserModel]:
        """Get detailed user info."""
        return UserRepository.get_by_id(user_id)

    @staticmethod
    def add_role(user_id: int, role_name: str, requester_id: int) -> str:
        """Add a role to a user."""
        if role_name not in UserManagementService.VALID_ROLES:
            raise ValueError("نقش نامعتبر است.")

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")

        existing = UserRoleModel.query.filter_by(user_id=user_id, role=role_name).first()
        if existing:
            raise ValueError("این کاربر قبلاً این نقش را دارد.")

        db.session.add(UserRoleModel(user_id=user_id, role=role_name))
        db.session.commit()
        return "added"

    @staticmethod
    def remove_role(user_id: int, role_name: str, requester_id: int) -> str:
        """Remove a role from a user."""
        if role_name not in UserManagementService.VALID_ROLES:
            raise ValueError("نقش نامعتبر است.")

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")

        role = UserRoleModel.query.filter_by(user_id=user_id, role=role_name).first()
        if not role:
            raise ValueError("این کاربر این نقش را ندارد.")

        db.session.delete(role)
        db.session.commit()
        return "removed"

    @staticmethod
    def toggle_role(user_id: int, role_name: str) -> str:
        """Legacy toggle role. Only for organizer/arbiter."""
        if role_name not in ["organizer", "arbiter"]:
            raise ValueError("نقش نامعتبر است.")

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")

        existing_role = UserRoleModel.query.filter_by(user_id=user_id, role=role_name).first()
        if existing_role:
            db.session.delete(existing_role)
            db.session.commit()
            return "removed"
        else:
            db.session.add(UserRoleModel(user_id=user_id, role=role_name))
            db.session.commit()
            return "added"

    @staticmethod
    def toggle_admin(user_id: int, requester_id: int) -> str:
        """Toggle system admin status with last-admin protection."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")

        if user.is_admin:
            # Check if this is the last admin
            admin_count = UserModel.query.filter_by(is_admin=True).count()
            if admin_count <= 1:
                raise ValueError("امکان حذف آخرین ادمین سیستم وجود ندارد.")

            if user_id == requester_id:
                raise ValueError("شما نمی‌توانید دسترسی ادمین خود را حذف کنید. لطفاً از طریق ادمین دیگری اقدام کنید.")

            user.is_admin = False
            db.session.commit()
            return "removed"
        else:
            user.is_admin = True
            db.session.commit()
            return "added"