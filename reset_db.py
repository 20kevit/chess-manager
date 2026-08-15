from app import create_app
from app.extensions import db
import os

app = create_app()
with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables with new schema...")
    db.create_all()
    print("Done! Database is now clean and updated.")