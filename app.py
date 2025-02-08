from flask import Flask, render_template, session, redirect, request
from dotenv import load_dotenv
from os import getenv
from functools import wraps
from supabase import create_client
from uuid import uuid4
from requests import post

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
MEGABYTE = (2 ** 10) ** 2
app.config['MAX_FORM_MEMORY_SIZE'] = 10 * MEGABYTE

supabase_url = getenv("SUPABASE_URL")
supabase_key = getenv("SUPABASE_KEY")
supabase_secret_key = getenv("SUPABASE_SECRET_KEY")
recaptcha_secret_key = getenv("RECAPTCHA_SECRET_KEY")
recaptcha_site_key = getenv("RECAPTCHA_SITE_KEY")
supabase_client = create_client(supabase_url, supabase_key)

def protected(account):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if account == "admin":
                if session.get("admin"):
                    return func(*args, **kwargs)
            else:
                if session.get("admin") or session.get("user_email"):
                    return func(*args, **kwargs)
            return redirect("/login")

        return wrapper

    return decorator


@app.get("/")
def index():
    email = session.get("email")
    return render_template("index.html", email=email)


@app.route("/login", methods=["GET", "POST"])
def login():
    status, message, redirect_url = None, None, None
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        if (email, password) == ("admin@mail.com", "admin"):
            session["admin"] = True
            status, message, redirect_url = True, "Succesful login", "/admin"
        else:
            data = supabase_client.auth().sign_in_with_password(
                {"email": email, "password": password}
            )
            if data.user:
                user = data.user
                session["user_id"] = user.id
                session["user_email"] = user.email
                session["access_token"] = data.session.access_token
                session["email"] = email
                status, message, redirect_url = True, "Succesful login", "/home"
            else:
                status, message = False, "Wrong email or password"
    if redirect_url:
        return render_template(
            "login.html", message=message, status=status, redirect_url=redirect_url
        )
    return render_template("login.html", message=message, status=status)


@app.route("/register", methods=["GET", "POST"])
def register():
    message, status, redirect_url = None, None, None
    if request.method == "POST":
        recaptcha_response = request.form.get('g-recaptcha-response')
        if recaptcha_response:
            payload = {
                'secret': recaptcha_secret_key,
                'response': recaptcha_response
            }
            response = post('https://www.google.com/recaptcha/api/siteverify', data=payload).json()
            if response.get("success"):
                email, password = request.form["email"], request.form["password"]
                response = supabase_client.auth.sign_up({"email": email, "password": password})
                status = "success"
                message = "Succesful registered"
            else:
                status = "error"
                message = "Wrong captcha"
        else:
            status = "error"
            message = "Please complete captcha"
    if redirect_url:
        return render_template("register.html", status=status, message=message, redirect_url=redirect_url)
    return render_template("register.html", message=message, status=status)


@app.route("/logout", methods=["POST"])
def logout():
    supabase_client.auth().sign_out()
    session.clear()
    return redirect("login")

@app.get("/home")
@protected("user")
def home():
    return render_template("home.html")


@app.get("/home/chat")
@protected("user")
def chat():
    return render_template("chat.html")


@app.route("/home/create", methods=["GET", "POST"])
# @protected("user")
def create():
    if request.method == "POST":
        id = str(uuid4())
        title = request.form["title"]
        city = request.form["city"]
        description = request.form["description"]
        image = request.files["image"]
        image_path = f"public/{id}.png"
        supabase_admin = create_client(supabase_url, supabase_secret_key)
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
    return render_template("create.html")

@app.errorhandler(413)
def request_entity_too_large(error):
    return 'File Too Large', 413

@app.get("/admin")
@protected("admin")
def admin():
    return render_template("admin.html")


@app.errorhandler(404)
def page404(error):
    return render_template("page404.html"), 404


@app.errorhandler(500)
def page500(error):
    return render_template("page500.html"), 505
