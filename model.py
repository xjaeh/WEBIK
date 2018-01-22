from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context

db = SQL("sqlite:///WEBIK.db")

def register(username, hash, fullname, work, search, email):

    users = db.execute("SELECT * FROM users")
    usernames = [user["username"] for user in users]
    emails = [user["email"] for user in users]
    if username in usernames:
        return 1
    if email in emails:
        return 2

    inserting = db.execute("INSERT INTO users (username,hash,fullname, work, search, email) VALUES \
                            (:username, :hash, :fullname, :work, :search, :email)", username = username, \
                            hash=hash, fullname = fullname, work = work, search = search, email=email)

def login(username, hash):

    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    if len(rows) != 1 or not pwd_context.verify(hash, rows[0]["hash"]):
        return False
    else:
        return id

def account():
    # let's the user change it's personal information

    # changes users full name if the user submitted one
    if request.form.get("fullname"):
        db.execute("UPDATE users SET fullname = :fullname WHERE id = :id" , \
        fullname = request.form.get("fullname"), id = session["user_id"], )

    # changes the password if the user submitted one
    if request.form.get("password"):
        # checks if the password and passwordconfirmation are the same
        if request.form.get("password") != request.form.get("confirmpassword"):
            apology("passwords don't match")
        else:
            # changes the users full name in the database
            db.execute("UPDATE users SET hash = :hash WHERE id = :id" , \
            hash = pwd_contect.hash(request.form.get("password")), id = session["user_id"], )

    # changes the users email if the user submitted one
    if request.form.get("email"):
        db.execute("UPDATE users SET email = :email WHERE id = :id" , \
        email = request.form.get("email"), id = session["user_id"], )

     # changes the users profession is the user submitted one
    if request.form.get("PLACEHOLDER"):
        db.execute("UPDATE users SET PLACEHOLDER = :PLACEHOLDER WHERE id = :id" , \
        fullname = request.form.get("PLACEHOLDER"), id = session["user_id"], )

    """
    Functie: profile(id):
    	returned Profile of None
    Beschrijving: bewerken van profiel zoals plaatsen van foto’s en profielfoto wijzigen.

    """
    def profile():
        # if user submits a new profilepicture, update profile pic

        # if user submits a photo (or multiple) add picture to users row in the database

        return db.execute("SELECT picture FROM pictures WHERE id=1")