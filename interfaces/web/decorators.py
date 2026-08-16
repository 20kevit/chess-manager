# interfaces/web/decorators.py
from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """دکوریتوری برای محدود کردن دسترسی به روت‌های خاص بر اساس نقش کاربر"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401) # Unauthorized
            if not current_user.has_any_role(list(roles)):
                abort(403) # Forbidden
            return f(*args, **kwargs)
        return wrapped
    return decorator