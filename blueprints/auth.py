from flask import Blueprint, request, session, render_template, redirect
from .supabase_module import supabase_client
from dotenv import load_dotenv
from os import getenv
from requests import post

load_dotenv()

recaptcha_secret_key = getenv("RECAPTCHA_SECRET_KEY")
recaptcha_site_key = getenv("RECAPTCHA_SITE_KEY")

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.route("/login", methods=["GET", "POST"])
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
            "auth/login.html", message=message, status=status, redirect_url=redirect_url
        )
    return render_template("auth/login.html", message=message, status=status)


@auth_blueprint.route("/register", methods=["GET", "POST"])
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
    return render_template("auth/register.html", message=message, status=status)


@auth_blueprint.route("/logout", methods=["POST"])
def logout():
    # supabase_client.auth().sign_out()
    session.clear()
    return redirect("login")
