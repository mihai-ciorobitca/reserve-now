from flask import Blueprint, render_template, session, redirect
from functools import wraps
from .supabase_module import supabase_admin

admin_blueprint = Blueprint("admin", __name__)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("admin"):
            return func(*args, **kwargs)
        return redirect("/auth/login")
    return wrapper


@admin_blueprint.get("/admin")
@login_required
def admin():
    response = (
        supabase_admin.table("posts")
        .select("title, city, description, public_url")
        .execute()
    )
    posts = response.data
    return render_template("admin/admin.html", posts=posts)