from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import datetime

from helpers import *
from model import *

# configure application
app = Flask(__name__)

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def mainroute():
    return render_template("main.html")

@app.route("/register", methods=["GET", "POST"])
def registerroute():
    if request.method == "POST":
        if request.form.get("work") == "I am a ...":
            return apology("register.html","Please fill your profession in")

        if request.form.get("search") == "I am looking for a ...":
            return apology("Please fill in what you're looking for")
        return render_template("workspace.html")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def loginroute():
    return render_template("login.html")

@app.route("/logout")
def logoutroute():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to main
    return redirect(url_for("main"))

@app.route("/workspace", methods=["GET", "POST"])
#@login_required
def workspaceroute():
    return render_template("workspace.html")

@app.route("/howitworks", methods=["GET", "POST"])
def howitworksroute():
    return render_template("howitworks.html")

@app.route("/find", methods=["GET", "POST"])
#@login_required
def findroute():

        return render_template("find.html")

@app.route("/profile", methods=["GET", "POST"])
#@login_required
def profileroute():
    # if user reached route via POST (as by submitting a form via POST)
    pictures = profile()
    return render_template("profile.html",pictures=pictures)

@app.route("/account", methods=["GET", "POST"])
#@login_required
def accountroute():
    if request.method == "POST":
        account()
    else:
        return render_template("account.html")

@app.route("/upload", methods=["GET", "POST"])
#@login_required
def uploadroute():
    return render_template("upload.html")
