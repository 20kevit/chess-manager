# application/admin_service.py
from typing import List
from app.extensions import db
from infrastructure.db_models import UserModel, UserRoleModel
from infrastructure.repositories import UserRepository

class AdminService:

    @staticmethod
    def get_all_users() -> List[UserModel]:
        return UserModel.query.order_by(UserModel.email).all()

    @staticmethod
    def toggle_role(user_id: int, role_name: str) -> str:
        """Add or remove a role for a user. Returns 'added' or 'removed'."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("کاربر یافت نشد.")
        
        if role_name not in ["organizer", "arbiter"]:
            raise ValueError("نقش نامعتبر است.")

        existing_role = UserRoleModel.query.filter_by(user_id=user_id, role=role_name).first()
        if existing_role:
            db.session.delete(existing_role)
            db.session.commit()
            return "removed"
        else:
            db.session.add(UserRoleModel(user_id=user_id, role=role_name))
            db.session.commit()
            return "added"