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

        if check == "x":
            return apology("register.html", "Username already exist")
        if check == "y":
            return apology("register.html", "Email already exist")
        else:
            session["user_id"] = check
        return render_template("workspace.html")
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def loginroute():
    #allows the user to log in

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
@login_required
def workspaceroute():
    return render_template("workspace.html")

@app.route("/howitworks", methods=["GET", "POST"])
def howitworksroute():
    return render_template("howitworks.html")

@app.route("/find", methods=["GET", "POST"])
@login_required
def findroute():
    status = "temporary"
    id = session.get("user_id")
    finding=find(id)

    if request.method == "POST":

        accept = request.form.get('accept')
        reject = request.form.get('reject')
        if accept:
            status= "true"
        if reject:
            status= "false"
        statusupdate(id,finding,status)

        return redirect(url_for("findroute"))
    else:
        if finding == 'empty':
            return apology("find.html", "no more matches available")
        pictures = profile(finding)
        return render_template("find.html",pictures=pictures)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profileroute():
    # if user reached route via POST (as by submitting a form via POST)
    id = session.get("user_id")
    pictures = profile(id)
    return render_template("profile.html",pictures=reversed(pictures))


@app.route("/account", methods=["GET", "POST"])
@login_required
def accountroute():
    # let's the user change his/her personel information
    if request.method == "POST":

    if request.method == "POST":

        # checks if fullname is made up of at least 2 words
        if request.form.get("fullname"):
            if " " not in request.form.get("fullname") and len(request.form.get("fullname") < 3):
                return apology("account.html", "please fill in your full name")

        # checks if email is valid
        if request.form.get("email"):
            if "@" not in request.form.get("email") or "." not in request.form.get("email"):
                return apology("please fill in a valid email adress")

        # changes the users information, returns an integer in case of an error
        errorcode = account(request.form.get("fullname"), request.form.get("old password"), request.form.get("password"), \
        request.form.get("confirmpassword"), request.form.get("email"), request.form.get("work"), request.form.get("search"))

        # tells the user what error occured
        if errorcode == 0:
            return apology("account.html", "please fill in at least two words in full name")
        if errorcode == 1:
            return apology("account.html", "please fill in old password, new pasword and confirm password")
        if errorcode == 2:
            return apology("account.html", "please make sure new password and password confirmation are the same")
        if errorcode == 3:
            return apology("account.html", "old password invalid")

        # redirects the user if there was no error
        else:
            return redirect(url_for("workspaceroute"))

    else:
        return render_template("account.html")



@app.route("/upload", methods=["GET", "POST"])
@login_required
def uploadroute():
    # allows the user to upload a photo to his/her profile by uploading alocal file or giving a URL
    if request.method == "POST" and "photo"in request.files:
        if request.form.get("url"):
            filename = request.form.get("url")
        else:
            filename = photos.save(request.files['photo'])
        id = session.get("user_id")
        upload(filename, id)
        return redirect(url_for("profileroute"))

    else:
        return render_template("upload.html")

@app.route("/delete", methods=["GET", "POST"])
@login_required
def deleteroute():
    # allows the user to delete a picture from his/her profile
    id = session.get("user_id")
    picture = request.form.get("delete")
    selection = select(id)

    if request.method == "POST":
        delete(picture, id)
        return redirect(url_for("profileroute"))
    else:
        return render_template("delete.html", rows = selection)

@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpasswordroute():
    # allows the user to request a new password

    if request.method == "POST":
        # ensures the user filled in all forms
        if not request.form.get("username") or not request.form.get("email"):
            return apology("forgotpassword.html", "please fill in all fields")
        else:
            # changes the users password in the database and sends the user an email with his/her new password, or returns an integer in case of an error
            errorcode = retrievepassword(request.form.get("username"), request.form.get("email"))

        # tells the user what error occured
        if errorcode == 0:
            return apology("forgotpassword.html", "username incorrect")
        if errorcode == 1:
            return apology("forgotpassword.html", "email incorrect")
        # redirects the user to mail_sent.html in case of no error
        else:
            return redirect(url_for("email_sentroute"))

    else:
        return render_template("forgotpassword.html")

@app.route("/email_sent", methods=["GET", "POST"])
def email_sentroute():
    # displays email_sent.html
    return render_template("email_sent.html")