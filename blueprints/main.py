from flask import Blueprint, session, render_template

main_blueprint = Blueprint("main", __name__)

@main_blueprint.get("/")
def index():
    email = session.get("email", False)
    admin = session.get("admin", False)
    print(email, admin)
    return render_template("index.html", email=email, admin=admin)