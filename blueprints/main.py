from flask import Blueprint, session, render_template

main_blueprint = Blueprint("main", __name__)

@main_blueprint.get("/")
def index():
    email = session.get("email")
    return render_template("index.html", email=email)