from flask import Flask, render_template, session, redirect, request
from flask_session import Session
from dotenv import load_dotenv
from os import getenv

load_dotenv()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

@app.get("/")
def index():
    if session.get("email"):
        return render_template("index.html")
    return redirect("/login")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        if (email, password) == ("admin@mail.com", "admin"):
            session["email"] = email
            return redirect("/dashboard")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    return render_template("register.html")

app.run(debug=True)