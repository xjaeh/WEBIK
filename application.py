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

# Initialize photo upload mechanism
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
    """ Renders homepage"""
    return render_template("main.html")


@app.route("/register", methods=["GET", "POST"])
def registerroute():
    """Allows user to register"""

    # If user reached route via POST
    if request.method == "POST":

        # Ensure username, password and password confirmation are filled in
        # Otherwise, returns apology
        if not request.form.get("username"):
            return apology("register.html", "Please fill in an username")

        if not request.form.get("password"):
            return apology("register.html", "Password is required for registration")

        if not request.form.get("confirmpassword"):
            return apology("register.html", "You must provide password confirmation")

        if request.form.get("password") != request.form.get("confirmpassword"):
            return apology("register.html", "Passwords do not match, try again")

        if not request.form.get("fullname") or " " not in request.form.get("fullname"):
            return apology("register.html", "Please fill in your first and last name")

        if not request.form.get("email"):
            return apology("register.html","Please fill in a email address")

        if request.form.get("work") == "I am a ...":
            return apology("register.html","Please fill your profession in")

        if request.form.get("search") == "I am looking for a ...":
            return apology("register.html","Please fill in what profession you're looking for")

        # Put infomation in database, if conditions apply
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
            return apology("register.html", "Error while sending mail to your email addres")

        # Remembers user id and logs in automatically
        else:
            session["user_id"] = check
        return render_template("workspace.html")

    # Else if user reached route via GET
    else:
        fullname = str(request.form.get("fullname"))
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

        # Checks username and password combination
        check = login(username=request.form.get("username"), hash=request.form.get("password"))

        # Returns apology if password and username don't match
        if check == False:
            return apology("login.html","Invalid username and password combination")

        # Else, redirect user to workspace
        else:
            session["user_id"] = check
        return redirect(url_for("workspaceroute"))

    # Else if user reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
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

    # Initialize variables
    status = "temporary"
    id = session.get("user_id")
    finding = find(id)

    # If user reaches route via POST
    if request.method == "POST":

        # Check if user clicked accept or reject
        accept = request.form.get('accept')
        reject = request.form.get('reject')
        if accept:
            status= "true"
        if reject:
            status= "false"

        # Update status of user and other user
        status_update(id,finding,status)

        # Check if the id's accepted eachother
        check = status_check(id,finding)
        if check == True:
            # sends email in case of match
            pair(id,finding)
            inform_match(id,finding)
        return redirect(url_for("findroute"))

    # If user reached route via GET
    else:
        # Return apology when no more matches are availible
        if finding == 'empty':
            return apology("find.html", "No more matches available")

        # Else, shows a random profile from the list of possible matches
        else:
            pictures = select(finding)
            pictures = pictures[-6:]
            work = find_work(id,finding)
            length = len(pictures)
            return render_template("find.html", pictures=reversed(pictures), \
                                    work=work, length=length)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profileroute():
    """Display user's profile """

    id = session.get("user_id")
    pictures = profile(id)
    length = len(pictures)
    fullname = profile_fullname(id)

    return render_template("profile.html",pictures=reversed(pictures), \
                            fullname=fullname, length=length)


@app.route("/account", methods=["GET", "POST"])
@login_required
def accountroute():
    """Let user change his/her personal information"""

    # If user reaches route via POST
    if request.method == "POST":

        # Ensure fullname is filled in and made up of at least two words
        if request.form.get("fullname"):
            if " " not in request.form.get("fullname") and len(request.form.get("fullname") < 3):
                return apology("account.html", "Please fill in your full name")

        # Check if email is valid
        if request.form.get("email"):
            try:
                server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)

                # Creates a seperate  email for each person
                subject = "New password"

                with open("email_templates/change_password.txt", "r") as mail:
                    text = str(mail.read()).format(fullname)

                message = 'Subject: {}\n\n{}'.format(subject, text)

                server.login("collabstudiohelpdesk@gmail.com", "webikcollab")
                server.sendmail("collabstudiohelpdesk@gmail.com", email, message)

            except:
                return apology("account.html", \
                "Can't send email to that email adress")

        # Change personal information, return an errorcode in case of a problem
        errorcode = account(request.form.get("fullname"), \
                    request.form.get("old_password"),request.form.get("password"), \
                    request.form.get("confirm_password"), request.form.get("email"), \
                    request.form.get("work"), request.form.get("search"), \
                    request.form.get("extra_search"))

        # Tell user what error occured
        if errorcode == "error_fullname":
            return apology("account.html", \
            "Please fill in at least two words in full name")
        if errorcode == "error_password":
            return apology("account.html", \
            "Please fill in old password, new pasword and confirm password")
        if errorcode == "error_password_confirmation":
            return apology("account.html", \
            "Please make sure new password and password confirmation are the same")
        if errorcode == "error_password_verify":
            return apology("account.html", \
            "Old password invalid")

        # Else, redirect user to workspace
        else:
            return redirect(url_for("workspaceroute"))

    # If user reached route via GET
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
        elif request.files["photo"]:
            filename = photos.save(request.files['photo'])
        else:
            return apology("upload.html", "please select a photo")

        # Function that saves filename to database
        upload(filename, id)
        return redirect(url_for("profileroute"))

    # Else if user reached route via GET
    else:
        return render_template("upload.html")


@app.route("/delete", methods=["GET", "POST"])
@login_required
def deleteroute():
    """Allows the user to delete a picture from his/her profile"""

    # Initialise variables
    id = session.get("user_id")
    picture = request.form.get("delete")
    selection = select(id)

    # If user reached rout via POST
    if request.method == "POST":
        delete(picture, id)
        return redirect(url_for("profileroute"))

    # Else if user reached route via GET
    else:
        return render_template("delete.html", rows = selection)


@app.route("/forgotpassword", methods=["GET", "POST"])
def forgotpasswordroute():
    """Allows the user to request a new password"""

    # If user reached rout via POST
    if request.method == "POST":
        # Ensures the user filled in all forms
        if not request.form.get("username") or not request.form.get("email"):
            return apology("forgotpassword.html", "Please fill in all fields")
        else:
            # Changes the users password in the database and sends the user an email
            errorcode = retrieve_password(request.form.get("username"), request.form.get("email"))

        # Tells the user what error occured
        if errorcode == 0:
            return apology("forgotpassword.html", "Username incorrect")
        if errorcode == 1:
            return apology("forgotpassword.html", "Email incorrect")
        # Redirects the user to mail_sent.html in case of no error
        else:
            return redirect(url_for("email_sentroute"))

    # Else if user reached route via GET
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

    id = session.get("user_id")
    # Create a dict of all users the user matched with
    contact = contacts(id)

    # If user reached route via POST
    if request.method == "POST":

        # Create a list of all id's of all users the user matched with
        ids=[str(person["other_id"]) for person in contact]

        # If the user clicked on the "info" in a chatroom, render that user's profile
        for item in ids:
            if request.form.get(item) == "Info":
                fullname = profile_fullname(int(item))
                pictures = profile(int(item))
                length = len(pictures)
                return render_template("profile2.html",fullname=fullname, \
                                        pictures=reversed(pictures), length=length)
            elif request.form.get(item):
                session["other_id"] = item

        other_id = session.get("other_id")
        # Send the user's message, id the user submitted one
        if request.form.get("message"):
            message = request.form.get("message")
            chat(id, other_id, message)
        messages = conversation(id, other_id)

        # Refreshes the chat
        return render_template("chat.html", contacts=contact,messages=messages, \
                                id=id, other_id=int(other_id))

    # Else if user reached route via GET
    else:
        # Open chatroom on first contact in contact
        try:
            other_id = contact[0]["other_id"]
        # If user has no contacts, render chat2.html
        except:
            return render_template("chat2.html")

        if session.get("other_id") == None:
            session["other_id"] = other_id
        other_id = session.get("other_id")
        messages = conversation(id, other_id)

        return render_template("chat.html", contacts=contact,messages=messages, \
                                id=id, other_id=int(other_id))
