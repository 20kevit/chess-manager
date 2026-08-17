from functools import wraps
from flask import abort, redirect, url_for, flash, request
from flask_login import current_user

def role_required(*roles):
    """Decorator to restrict access to specific roles. Redirects to login if unauthenticated."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.has_any_role(list(roles)):
                flash("شما دسترسی به این بخش را ندارید.", "error")
                return redirect(url_for('dashboard.index'))
                
            return f(*args, **kwargs)
        return wrapped
    return decorator