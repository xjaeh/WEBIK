from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import datetime

from helpers import *
from model import *

# configure application
app = Flask(__name__)

photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

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
            return apology("register.html","Please fill in an username")

        if not request.form.get("password"):
            return apology("register.html","Password is required for registration")

        if not request.form.get("confirmpassword"):
            return apology("register.html","You must provide password confirmation")

        if request.form.get("password") != request.form.get("confirmpassword"):
            return apology("register.html","Passwords do not match, try again")

        if not request.form.get("fullname") or " " not in request.form.get("fullname"):
            return apology("register.html","Please fill in your first and last name")

        if not request.form.get("email") or "@" not in request.form.get("email") or "." not in request.form.get("email"):
            return apology("register.html","Please fill in a valid email address")

        if request.form.get("work") == "I am a ...":
            return apology("register.html","Please fill your profession in")

        if request.form.get("search") == "I am looking for a ...":
            return apology("register.html","Please fill in what profession you're looking for")

        check = register(request.form.get("username"), pwd_context.hash(request.form.get("password")), request.form.get("fullname"), \
                request.form.get("work"), request.form.get("search"), request.form.get("email"))

        if check == 1:
            return apology("register.html", "Username already exist")
        if check == 2:
            return apology("register.html", "Email already exist")
        else:
            session["user_id"] = check
        return render_template("workspace.html")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def loginroute():

    session.clear()

    if request.method == "POST":

        # Ensure username is submitted
        if not request.form.get("username"):
            return apology("login.html","Must provide username")

        elif not request.form.get("password"):
            return apology("login.html","Must provide valid password")

        test = login(username=request.form.get("username"), hash=request.form.get("password"))

        if test == False:
            return apology("login.html","Invalid username and password combination")
        else:
            session["user_id"] = test
        return redirect(url_for("workspaceroute"))

    else:
        return render_template("login.html")


@app.route("/logout")
def logoutroute():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to main
    return redirect(url_for("mainroute"))

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
        fullname = request.form.get("fullname")

        if request.form.get("password") != request.form.get("confirmpassword"):
            return apology("account.html","passwords don't match")
        else:
            password = request.form.get("password")

        email = request.form.get("email")

        account(fullname, password, email)
    else:
        return render_template("account.html")

@app.route("/upload", methods=["GET", "POST"])
#@login_required
def uploadroute():
    if request.method == "POST" and "photo"in request.files:

        filename = photos.save(request.files['photo'])
        id = 2
        upload(filename, id)
        return redirect(url_for("profileroute"))

    else:
        return render_template("upload.html")
