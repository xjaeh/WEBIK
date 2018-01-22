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

        # Ensure username, password and password confirmation are filled in, otherwise apology
        if not request.form.get("username"):
            return apology("Please fill in an username")

        if not request.form.get("password"):
            return apology("Password is required for registration")

        if not request.form.get("confirmpassword"):
            return apology("You must provide password confirmation")

        if request.form.get("password") != request.form.get("confirmpassword"):
            return apology("Passwords do not match, try again")

        if not request.form.get("fullname") or " " not in request.form.get("fullname"):
            return apology("Please fill in your first and last name")

        if not request.form.get("email") or "@" not in request.form.get("email") or "." not in request.form.get("email"):
            return apology("Please fill in a valid email address")

        if request.form.get("work") == "I am a ...":
            return apology("Please fill your profession in")

        if request.form.get("search") == "I am looking for a ...":
            return apology("Please fill in what profession you're looking for")


        #inserting = db.execute("INSERT INTO users (username,hash,fullname) VALUES \
        #                        (:username, :hash, :fullname)", username = request.form.get("username"), \
        #                        hash=pwd_context.hash(request.form.get("password")), fullname = request.form.get("fullname"))
        #if not inserting:
        #    return apology("Username already exist, please fill in another one")

        #insertemail = db.execute("INSERT INTO users (email) VALUES (:email)", email = request.form.get("email"))
        #if not insertemail:
        #    return apology("Email already exist, please fill in another one")


        #session = ["user_id"] = inserting
        return render_template("workspace.html")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def loginroute():

    session.clear()

    if request.method == "POST":

        # Ensure username is submitted
        if not request.form.get("username"):
            return apology("Must provide username")

        elif not request.form.get("password"):
            return apology("Must provide valid password")

        #rows = ("SELECT * FROM users WHERE username =:username", username = request.form.get("username"))

        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["hash"]):
            return apology("Invalid username/password combination")

        session["user_id"] = rows[0]["id"]
        return redirect(url_for("workspaceroute"))

    else:
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
