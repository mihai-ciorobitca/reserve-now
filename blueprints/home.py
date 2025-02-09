from flask import Blueprint, render_template, request, session, redirect
from uuid import uuid4
from functools import wraps
from .supabase_module import supabase_admin

home_blueprint = Blueprint("home", __name__)

def protected_home(account):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if account == "admin":
                if session.get("admin"):
                    return func(*args, **kwargs)
            else:
                if session.get("admin") or session.get("user_email"):
                    return func(*args, **kwargs)
            return redirect("/auth/login")
        return wrapper
    return decorator

@home_blueprint.get("/home")
# @protected_home("user")
def home():
    return render_template("home/home.html")


@home_blueprint.get("/home/chat")
# @protected_home("user")
def chat():
    return render_template("home/chat.html")


@home_blueprint.route("/home/create", methods=["GET", "POST"])
# @protected_home("user")
def create():
    if request.method == "POST":
        id = str(uuid4())
        title = request.form["title"]
        city = request.form["city"]
        description = request.form["description"]
        image = request.files["image"]
        image_path = f"public/{id}.png"
        supabase_admin.storage.from_("images").upload(
            file=image.read(),
            path=image_path,
            file_options={"content-type": image.content_type},
        )
        supabase_admin.table("posts").insert(
            {
                "title": title,
                "city": city,
                "description": description,
                "image_path": image_path,
            }
        ).execute()
    return render_template("home/create.html")
