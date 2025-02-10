from flask import Blueprint, render_template, request, session, redirect
from uuid import uuid4
from functools import wraps
from .supabase_module import supabase_admin
from os import getenv
from dotenv import load_dotenv

load_dotenv()

home_blueprint = Blueprint("home", __name__)


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if session.get("email"):
            return func(*args, **kwargs)
        return redirect("/auth/login")
    return wrapper



@home_blueprint.get("/home")
@login_required
def home():
    response = (
        supabase_admin.table("posts")
        .select("title, city, description, public_url")
        .neq("email", session["email"])
        .execute()
    )
    posts = response.data
    return render_template("home/home.html", posts=posts)


@home_blueprint.get("/home/chats")
@home_blueprint.get("/home/chats/<user_id>")
@login_required
def chat(user_id=None):
    supabase_url = getenv("SUPABASE_URL")
    supabase_anon_key = getenv("SUPABASE_ANON_KEY")
    chats = []
    return render_template(
        "home/chats.html",
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
        user_id=user_id,
        chats=chats,
    )


@home_blueprint.get("/home/my-posts")
@login_required
def my_posts():
    response = (
        supabase_admin.table("posts")
        .select("title, city, description, public_url")
        .eq("email", session["email"])
        .execute()
    )
    posts = response.data
    return render_template("home/my-posts.html", posts=posts)


@home_blueprint.route("/home/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        id = str(uuid4())
        user_id = session["id"]
        title = request.form["title"]
        city = request.form["city"]
        post_type = request.form["type"]
        description = request.form["description"]
        image = request.files["image"]
        image_path = f"public/{id}.png"
        supabase_admin.storage.from_("images").upload(
            file=image.read(),
            path=image_path,
            file_options={"content-type": image.content_type},
        )
        public_url = supabase_admin.storage.from_("images").get_public_url(image_path)
        print(public_url)
        supabase_admin.table("posts").insert(
            {
                "user_id": user_id,
                "title": title,
                "city": city,
                "type": post_type,
                "email": session["email"],
                "description": description,
                "public_url": public_url,
            }
        ).execute()
        return redirect("/home/my-posts")
    return render_template("home/create.html")
