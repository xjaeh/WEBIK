from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import datetime

from helpers import *

# configure application
app = Flask(__name__)
db = SQL("sqlite:///WEBIK.db")

# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.route("/")
def mainroute():
    return render_template("main.html")

@app.route("/register", methods=["GET", "POST"])
def registerroute():
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

        return render_template("profile.html")

@app.route("/account", methods=["GET", "POST"])
#@login_required
def accountroute():
    account()

        return render_template("account.html")
