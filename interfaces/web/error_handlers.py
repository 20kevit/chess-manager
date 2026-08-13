"""
Centralized error handling for routes.
"""
import traceback
from flask import flash, redirect, request
from functools import wraps


def handle_route_errors(f):
    """Decorator for route handlers that catches and flashes errors."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            flash(str(e), "error")
            return redirect(request.referrer or "/")
        except Exception as e:
            traceback.print_exc()
            flash(f"خطا: {str(e)}", "error")
            return redirect(request.referrer or "/")
    return wrapper