from app.extensions import db
from infrastructure.db_models import UserModel, UserRoleModel
admin = UserModel(email="test@test.com")
admin.set_password("test1234")
admin.is_admin = True
db.session.add(admin)
db.session.commit()