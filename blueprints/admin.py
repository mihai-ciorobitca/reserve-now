from flask import Blueprint, render_template, session, redirect, request
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


@admin_blueprint.get("/")
@login_required
def admin():
    response = (
        supabase_admin.table("posts")
        .select("title, city, description, public_url, id")
        .execute()
    )
    posts = response.data
    return render_template("admin/admin.html", posts=posts)

@admin_blueprint.post("/delete-post")
@login_required
def admin_delete_post():
    id = request.form["id"]
    response = (
        supabase_admin.table("posts")
        .delete()
        .eq("id", id)
        .execute()
    )
    return redirect("/admin")