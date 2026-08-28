"""
User Repository.
"""
from typing import Optional

from app.extensions import db

from infrastructure.models.user import UserModel, UserRoleModel

class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> Optional[UserModel]:
        return UserModel.query.get(user_id)

    @staticmethod
    def get_by_email(email: str) -> Optional[UserModel]:
        return UserModel.query.filter_by(email=email.lower()).first()

    @staticmethod
    def save(user: UserModel) -> UserModel:
        db.session.add(user)
        db.session.flush()
        return user

    @staticmethod
    def add_role(user: UserModel, role_name: str):
        existing = UserRoleModel.query.filter_by(user_id=user.id, role=role_name).first()
        if not existing:
            new_role = UserRoleModel(user_id=user.id, role=role_name)
            db.session.add(new_role)
            db.session.flush()