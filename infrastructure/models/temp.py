"""
Temporary Import Data Model.
"""
from datetime import datetime
from app.extensions import db


class TempImportDataModel(db.Model):
    __tablename__ = "temp_import_data"
    __table_args__ = {"mysql_charset": "utf8mb4", "mysql_collate": "utf8mb4_unicode_ci"}

    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.String(64), unique=True, nullable=False, index=True)
    data_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)