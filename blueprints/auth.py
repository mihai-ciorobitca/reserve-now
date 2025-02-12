from flask import Blueprint, request, session, render_template, redirect, jsonify
from .supabase_module import supabase_admin
from dotenv import load_dotenv
from os import getenv
from requests import post
from gotrue.errors import AuthApiError

load_dotenv()

recaptcha_secret_key = getenv("RECAPTCHA_SECRET_KEY")
recaptcha_site_key = getenv("RECAPTCHA_SITE_KEY")
admin_email = getenv("ADMIN_EMAIL")

auth_blueprint = Blueprint("auth", __name__)


@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            data = request.get_json()
            email = data.get("email")
            password = data.get("password")
            response = supabase_admin.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if response:
                user = response.user
                if user.email == admin_email:
                    session["admin"] = True
                    redirect_url = "/admin"
                else:
                    session["email"] = email
                    session["username"] = user.email.split("@")[0]
                    session["id"] = user.id
                    session["access_token"] = response.session.access_token
                    session["refresh_token"] = response.session.refresh_token
                    redirect_url = "/home"
                return (
                    jsonify(
                        {"message": "Succesful login", "redirect_url": redirect_url}
                    ),
                    200,
                )
            else:
                print(response)
                return jsonify({"message", response}), 400
        except AuthApiError as e:
            return jsonify({"message": str(e)}), 400
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    return render_template("auth/login.html")


@auth_blueprint.route("/login/google")
def google_login():
    response = supabase_admin.auth.sign_in_with_oauth(
        {
            "provider": "google",
            "options": {"redirect_to": f"{request.host_url}auth/google/callback"},
        }
    )
    return redirect(response.url)


@auth_blueprint.route("/google/callback")
def callback():
    code = request.args.get("code")
    next = request.args.get("next", "/home")
    if code:
        response = supabase_admin.auth.exchange_code_for_session({"auth_code": code})
        user = response.user
        session["email"] = user.email
        session["username"] = user.email.split("@")[0]
        session["id"] = user.id
    return redirect(next)


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            data = request.get_json()
            recaptcha_response = data.get("recaptcha_response")
            if recaptcha_response:
                payload = {
                    "secret": recaptcha_secret_key,
                    "response": recaptcha_response,
                }
                response = post(
                    "https://www.google.com/recaptcha/api/siteverify", data=payload
                ).json()
                if response.get("success"):
                    email = data.get("email")
                    password = data.get("password")
                    response = supabase_admin.auth.admin.create_user(
                        {
                            "email": email,
                            "password": password,
                            "user_metadata": {"email": email},
                        }
                    )
                    if response:
                        response = supabase_admin.auth.admin.invite_user_by_email(
                            email,
                            options={
                                "redirect_to": "https://reserve-now.onrender.com/auth/login"
                            },
                        )
                        if response:
                            return (
                                jsonify(
                                    {
                                        "message": "User created. Check email for verification"
                                    }
                                ),
                                200,
                            )
                        else:
                            return jsonify({"message": response}), 200
                    return jsonify({"message": response}), 200
                return jsonify({"message": "Wrong captcha"}), 400
            return jsonify({"message": "Please complete captcha"}), 400
        except AuthApiError as e:
            return jsonify({"message": str(e)}), 400
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    return render_template("auth/register.html")


@auth_blueprint.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        try:
            data = request.get_json()
            email = data["email"]
            response = supabase_admin.auth.reset_password_for_email(
                email,
                {
                    "redirect_to": "https://reserve-now.onrender.com/auth/update-password",
                },
            )
            if response:
                return jsonify({"message": "Reset email link sent"}), 200
            return jsonify({"message": response}), 400
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    return render_template("auth/reset-password.html") 

@auth_blueprint.route("/update-password", methods=["GET", "POST"])
def update_password():
    if request.method == "POST":
        try:
            data = request.get_json()
            new_password = data["new_password"]
            response = supabase_admin.auth.update_user(
                {"password": new_password}
            )
            if response:
                return jsonify({"message": "Password changed"}), 200
            return jsonify({"message": response}), 400
        except Exception as e:
            return jsonify({"message": str(e)}), 400
    return render_template("auth/update-password.html") 

@auth_blueprint.post("/logout")
def logout():
    supabase_admin.auth.sign_out()
    session.clear()
    return redirect("/home")
