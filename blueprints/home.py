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
        if session.get("email") and session.get("username"):
            return func(*args, **kwargs)
        session.clear()
        return redirect("/auth/login")

    return wrapper


@home_blueprint.get("/")
@login_required
def home():
    response = (
        supabase_admin.table("posts")
        .select("*")
        .neq("email", session["email"])
        .execute()
    )
    posts = response.data
    username = session["email"].split("@")[0]
    return render_template("home/home.html", posts=posts, username=username)


@home_blueprint.get("/chats")
@login_required
def chat_get():
    supabase_url = getenv("SUPABASE_URL")
    supabase_anon_key = getenv("SUPABASE_ANON_KEY")
    
    access_token = session.get("access_token", False)
    refresh_token = session.get("refresh_token", False)
    if not access_token or not refresh_token:
        supabase_admin.auth.sign_out()
        session.clear()
        return redirect("/home")
    
    sender_id = session["id"]
    sender_username = session["email"].split("@")[0]
    
    response = (
        supabase_admin.table("messages")
        .select("receiver_username, receiver_id, sender_id, sender_username")
        .or_(f"sender_id.eq.{sender_id},receiver_id.eq.{sender_id}")
        .execute()
    )
    data = response.data
    
    chats = {}
    for item in data:
        if item["sender_id"] == sender_id:
            chats[item["receiver_id"]] = item["receiver_username"]
        else:
            chats[item["sender_id"]] = item["sender_username"]
    if session.get("current_receiver", False):
        chats[session["current_receiver"][0]]=session["current_receiver"][1]
                
    return render_template(
        "home/chats.html",
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
        chats=chats,
        sender_id=sender_id,
        sender_username=sender_username,
        access_token = access_token,
        refresh_token = refresh_token
    )


@home_blueprint.post("/chats")
@login_required
def chat_post():
    user_id = request.form["user_id"]
    username = request.form["username"]
    supabase_admin.auth.sign_out()
    session["current_receiver"] = (user_id, username)
    return redirect("/home/chats")


@home_blueprint.get("/my-posts")
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


@home_blueprint.route("/create", methods=["GET", "POST"])
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
        supabase_admin.table("posts").insert(
            {
                "user_id": user_id,
                "title": title,
                "city": city,
                "type": post_type,
                "email": session["email"],
                "description": description,
                "public_url": public_url,
                "username": session["email"].split("@")[0],
            }
        ).execute()
        return redirect("/home/my-posts")
    return render_template("home/create.html")
