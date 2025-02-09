from flask import Blueprint, render_template, session, redirect
from functools import wraps

admin_blueprint = Blueprint("admin", __name__)

def protected_admin():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if session.get("admin"):
                return func(*args, **kwargs)
            return redirect("/login")
        return wrapper
    return decorator

@admin_blueprint.get("/admin")
# @protected_admin()
def admin():
    return render_template("admin/admin.html")