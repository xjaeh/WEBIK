from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import datetime
from helpers import *
from model import *

# Configure application
app = Flask(__name__)

# Initialise photo upload mechanism
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/")
def mainroute():
    """ Returns homepage"""
    return render_template("main.html")

@app.route("/register", methods=["GET", "POST"])
def registerroute():
    """Allows user to register"""

    # If user reached route via POST
    if request.method == "POST":

        # Ensure username, password and password confirmation are filled in
        # Otherwise it returns apology
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

        if not request.form.get("email"):
            return apology("register.html","Please fill in a email address")

        if request.form.get("work") == "I am a ...":
            return apology("register.html","Please fill your profession in")

        if request.form.get("search") == "I am looking for a ...":
            return apology("register.html","Please fill in what profession you're looking for")

        # put infomation in database if conditions apply
        check = register(request.form.get("username"),
                pwd_context.hash(request.form.get("password")), \
                request.form.get("fullname"), request.form.get("work"), \
                request.form.get("search"), request.form.get("email"), \
                request.form.get("extra_search"))

        # Checks if username and email are not already used
        if check == "error_user":
            return apology("register.html", "Username already exist")
        elif check == "error_email":
            return apology("register.html", "Email already exist")
        elif check == 'error_invalid_mail':
            return apology("register.html", "Error while sending mail to your emailaddres")

        # Remembers user id and logs in automatically
        else:
            session["user_id"] = check
        return render_template("workspace.html")

    # Else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def loginroute():
    """Allows the user to log in"""

    # If user reached route via POST
    if request.method == "POST":

        # Ensures username  and password are submitted
        if not request.form.get("username"):
            return apology("login.html","Must provide username")

        elif not request.form.get("password"):
            return apology("login.html","Must provide valid password")

        # Function that checks username and password combination, otherwise apology
        check = login(username=request.form.get("username"), hash=request.form.get("password"))

        if check == False:
            return apology("login.html","Invalid username and password combination")

        # Redirects user to workspace if logged in correctly
        else:
            session["user_id"] = check
        return redirect(url_for("workspaceroute"))

    # Else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logoutroute():
    """Logs user out"""

    # Forgets any user_id
    session.clear()

    # Redirects user to main
    return redirect(url_for("mainroute"))


@app.route("/workspace", methods=["GET"])
@login_required
def workspaceroute():
    """Returns workspace template"""
    return render_template("workspace.html")


@app.route("/howitworks", methods=["GET"])
def howitworksroute():
    """Returns howitworks template"""
    return render_template("howitworks.html")


@app.route("/find", methods=["GET", "POST"])
@login_required
def findroute():
    """Displays the profile of a possible match"""

    # Initialises variables
    status = "temporary"
    id = session.get("user_id")
    finding=find(id)

    # If users reaches route via POST
    if request.method == "POST":

        # Checks if user clicked the accept or reject button
        accept = request.form.get('accept')
        reject = request.form.get('reject')
        if accept:
            status= "true"
        if reject:
            status= "false"

        # Function that changes the status of the two id'ss
        status_update(id,finding,status)

        # Function that checks if the id's accepted eachother and sends email
        check = status_check(id,finding)
        if check == True:
            inform_match(id,finding)
        return redirect(url_for("findroute"))

    # Else if user reached route via GET (as by clicking a link or via redirect)
    else:
        if finding == 'empty':
            return apology("find.html", "no more matches available")
        else:
            pictures = profile(finding)
            work = find_work(id,finding)
            return render_template("find.html", pictures=reversed(pictures), work=work)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profileroute():
    """Display users profile """

    id = session.get("user_id")
    pictures = profile(id)
    fullname = profile_fullname(id)
    return render_template("profile.html",pictures=reversed(pictures), fullname=fullname)

@app.route("/account", methods=["GET", "POST"])
@login_required
def accountroute():
    """Let's the user change his/her personel information"""

    # If the users reaches route via POST
    if request.method == "POST":

        # Checks if fullname is made up of at least 2 words
        if request.form.get("fullname"):
            if " " not in request.form.get("fullname") and len(request.form.get("fullname") < 3):
                return apology("account.html", "Please fill in your full name")

        # Checks if email is valid
        if request.form.get("email"):
            if "@" not in request.form.get("email") or "." not in request.form.get("email"):
                return apology("Please fill in a valid email adress")

        # Changes the users information, returns an integer in case of an error
        errorcode = account(request.form.get("fullname"), request.form.get("old password"), \
                    request.form.get("password"), request.form.get("confirmpassword"), \
                    request.form.get("email"), request.form.get("work"), request.form.get("search"), \
                    request.form.get("extra_search"))

        # Tells the user what error occured
        if errorcode == 0:
            return apology("account.html", "Please fill in at least two words in full name")
        if errorcode == 1:
            return apology("account.html", "Please fill in old password, new pasword and confirm password")
        if errorcode == 2:
            return apology("account.html", "Please make sure new password and password confirmation are the same")
        if errorcode == 3:
            return apology("account.html", "Old password invalid")

        # Redirects the user if there was no error
        else:
            return redirect(url_for("workspaceroute"))

    # Else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("account.html")

@app.route("/upload", methods=["GET", "POST"])
@login_required
def uploadroute():
    """Allows the user to upload a photo to his/her profile"""

    # If user reached route via POST
    if request.method == "POST" and "photo"in request.files:

        # Initialise id
        id = session.get("user_id")

        # Saves filename from url or from a local file
        if request.form.get("url"):
            filename = request.form.get("url")
        else:
            filename = photos.save(request.files['photo'])

        # Function that saves filename to database
        upload(filename, id)
        return redirect(url_for("profileroute"))

    # Else if user reached route via GET (as by clicking a link or via redirect)id = session.get("user_id")
    else:
        return render_template("upload.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def deleteroute():
    """Allows the user to delete a picture from his/her profile"""

    #initialise variables
    id = session.get("user_id")
    picture = request.form.get("delete")
    selection = select(id)

    # If user reached rout via POST
    if request.method == "POST":
        delete(picture, id)
        return redirect(url_for("profileroute"))

    # Else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("delete.html", rows = selection)


@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpasswordroute():
    """Allows the user to request a new password"""

    # If user reached rout via POST
    if request.method == "POST":
        # Ensures the user filled in all forms
        if not request.form.get("username") or not request.form.get("email"):
            return apology("forgotpassword.html", "please fill in all fields")
        else:
            # Changes the users password in the database and sends the user an email
            errorcode = retrieve_password(request.form.get("username"), request.form.get("email"))

        # Tells the user what error occured
        if errorcode == 0:
            return apology("forgotpassword.html", "username incorrect")
        if errorcode == 1:
            return apology("forgotpassword.html", "email incorrect")
        # Redirects the user to mail_sent.html in case of no error
        else:
            return redirect(url_for("email_sentroute"))

    # Else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("forgotpassword.html")


@app.route("/email_sent", methods=["GET"])
def email_sentroute():
    """displays email_sent.html"""
    return render_template("email_sent.html")

@app.route("/chat", methods=["GET", "POST"])
@login_required
def chatroute():
    """displays chat.html"""
    #id = session.get("user_id")
    id = 1
    contact = contacts(id)

    # if user reached route via POST
    if request.method == "POST":
        ids=[str(person["other_id"]) for person in contact]
        for item in ids:
            check = request.form.get(item)
            if check:
                session["other_id"] = item
        otherid = session.get("other_id")
        if request.form.get("message"):
            message = request.form.get("message")
            chat(id, otherid, message)
        messages = conversation(id, otherid)
        return redirect(url_for("chatroute"))

    else:
        otherid = contact[0]["other_id"]
        if session.get("other_id") == None:
            session["other_id"] = otherid
        otherid = session.get("other_id")
        messages = conversation(id, otherid)

        return render_template("chat.html", contacts=contact,messages=messages, id=id, otherid=otherid)