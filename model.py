import random
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context
from flask_session import Session
import smtplib
import random
import string
from flask import Flask, flash, redirect, render_template, request, session, url_for

# Initialises database
db = SQL("sqlite:///WEBIK.db")

def register(username, hash, fullname, work, search, email, extra_search):
    """Register machanism"""

    # Initialise variables
    users = db.execute("SELECT * FROM users")
    usernames = [user["username"] for user in users]
    emails = [user["email"] for user in users]

    # Checks if username and email already exists
    if username in usernames:
        return "error_user"
    elif email in emails:
        return "error_email"

    # Puts user information into the database
    else:
        db.execute("INSERT INTO users (username, hash, fullname, work, search, email, extra_search) VALUES \
                   (:username, :hash, :fullname, :work, :search, :email, :extra_search)", username=username, \
                    hash=hash, fullname=fullname, work=work, search=search, email=email, extra_search=extra_search)

    # Returns users id
    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    id = rows[0]["id"]
    return rows[0]["id"]

def login(username, hash):
    """Login mechanism"""

    # Checks username and password combination and returns False or id
    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    if len(rows) != 1 or not pwd_context.verify(hash, rows[0]["hash"]):
        return False
    else:
        return rows[0]["id"]

def account(fullname, old_password, password, confirm_password, email, work, search, extra_search):
    """Let's the user change his/her personal information"""

    # Changes users fullname if the user submitted one
    if fullname:
        if " " in fullname:
            db.execute("UPDATE users SET fullname=:fullname WHERE id=:id" , \
            fullname=fullname, id=session["user_id"], )
        else:
            return 0

    # Checks if all the passwordfields are filled in otherwise apology
    if password or confirm_password or old_password:
        if not old_password or not password or not confirm_password:
            return 1
        # Changes the password if the user submitted all passwords
        else:
            if password != confirm_password:
                return 3
            rows = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
            if pwd_context.verify(old_password, rows[0]["hash"]) == False:
                return 1
            else:
                db.execute("UPDATE users SET hash=:hash WHERE id=:id" , \
                    hash=pwd_context.hash(password), id=session["user_id"])

    # Changes the users email if the user submitted one
    if email:
        db.execute("UPDATE users SET email=:email WHERE id=:id" , \
        email=email, id=session["user_id"], )

    # Changes the users profession is the user submitted one
    if work and work != "I am a ...":
        db.execute("UPDATE users SET work=:work WHERE id=:id" , \
        work=work, id=session["user_id"], )

    # Changes the users search if the user submitted one
    if search and search != "I am looking for a ...":
        db.execute("UPDATE users SET search=:search WHERE id=:id" , \
        search=search, id=session["user_id"], )

    # Changes the users extra_search if the user submitted one
    if extra_search and extra_search != "Optional":
        db.execute("UPDATE users SET extra_search=:extra_search WHERE id=:id" , \
        extra_search=extra_search, id=session["user_id"], )

def profile(id):
    """Returns all photos under the users id in reverse order"""
    photos = db.execute("SELECT picture FROM pictures WHERE id=:id", id=id)
    return photos[::1]

def profile_fullname(id):
    """Returns fullname of user"""
    fullname = db.execute("SELECT fullname FROM users WHERE id=:id", id=id)
    return fullname

def upload(filename, id):
    """Lets the user upload a new photo and adds it to the database"""
    db.execute("INSERT INTO pictures (id, picture) VALUES (:id, :picture)", id=id, picture=filename)

def find(id):
    """Returns a potential match id"""

    # Selects search catogory from user and returns all users with the same work
    search = db.execute("SELECT search FROM users WHERE id=:id", id=id)
    extra_search = db.execute("SELECT extra_search FROM users WHERE id=:id", id=id)
    possible_matches = db.execute("SELECT id FROM users WHERE work=:search OR work=:extra_search", \
                                    search=search[0]["search"], extra_search=extra_search[0]["extra_search"])
    possible_matches_set = set(match["id"] for match in possible_matches)

    # Selects all the users which are already seen by the user
    already_seen= db.execute("SELECT otherid FROM matchstatus WHERE id=:id", id=id)
    already_seen_set= set(already["otherid"] for already in already_seen)

    # Returns a user id from possible_matches minus the ones already seen
    show = possible_matches_set - already_seen_set
    shows = [id for id in show]
    if shows == []:
        return 'empty'
    else:
        return random.choice(shows)

def find_work(id,finding):
    """Returns profession of user"""

    work = db.execute("SELECT work FROM users WHERE id=:id", id=finding)
    return work

def select(id):
    """Returns all pictures from the users id"""

    picture = db.execute("SELECT * FROM pictures WHERE id=:id", id=id)
    return picture

def delete(picture, id):
    """Lets the user remove a picture from the database"""

    return db.execute("DELETE FROM pictures WHERE picture=:picture", picture=picture)

def status_update(id,otherid,status):
    """Inserts status into database"""

    db.execute("INSERT INTO matchstatus (id, otherid, status) VALUES (:id, :otherid, :status)",\
                id=id, otherid=otherid, status=status)

def status_check(id, otherid, other_username):
    """Checks if two id's have a match"""

    # Selects the two statuses
    status1 = db.execute("SELECT status FROM matchstatus WHERE id=:id and otherid=:otherid", id=id, otherid=otherid)
    status2 = db.execute("SELECT status FROM matchstatus WHERE id=:id and otherid=:otherid", id=otherid, otherid=id)

    # Returns True or False depending upon mutual like or not
    try:
        status1[0]["status"] == "true" and status2[0]["status"] == "true"
        return True
        other_username = db.execute("SELECT username FROM users WHERE id=:otherid", id=otherid)
        db.execute("INSERT INTO pairs (id, other_id, other_username) VALUES (:id, :other_id, :other_username)", \
                    id=id, otherid=otherid, other_username=other_username)
    except:
        return False

def password_generator(chars=string.ascii_uppercase + string.digits):
    """Generate a random password with length 10"""
    return ''.join(random.choice(chars) for i in range(10))

def retrieve_password(username, email):
    """Allows the user to have a new password sent to them"""

    # Retrieves info for username and checks if username exists
    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    if not rows:
         return 0

    # Sends email if email is correct
    else:

        # Checks if email is correct and return error code
        if email != rows[0]["email"]:
            return 1
        else:
            # Generates a new password
            password = password_generator()

            # Changes password in database
            db.execute("UPDATE users SET hash =:hash WHERE username=:username" , \
                    hash = pwd_context.hash(password), username=username)

            # Sends new password to user and sets email structure
            server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
            subject = "Forgot password"
            text = "Hello, {}!\n\n your new password is: \n\n '{}' \n\n you can now use this password to log into your account. \n don't forget to change youer password after logging in.".format(rows[0]["fullname"], password)
            message = 'Subject: {}\n\n{}'.format(subject, text)

        # Sets up emailaccount
        server.login("tistacyhelpdesk@gmail.com", "webiktistacy")
        server.sendmail("tistacyhelpdesk@gmail.com", email, message)

def inform_match(id, otherid):
    """Sends new password to user and his/her match in case of a match"""

    # Selects user and match information
    user_info = db.execute("SELECT * FROM users WHERE id=:id", id=id)
    match_info = db.execute("SELECT * FROM users WHERE id=:id", id=otherid)

    # Sets up emailserver
    server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)

    # Creates a seperate  email for each person
    subject = "You got a match"
    text1 = """ Hello, {}!\n\n Congratulations! You and {} just got a match. Here's there emailadress:
             {} \n \n we hope you have a pleasant collaboration. \n \n Tistacy""".format(userinfo[0]["fullname"],\
            matchinfo[0]["fullname"], userinfo[0]["email"])
    message1 = 'Subject: {}\n\n{}'.format(subject, text1)

    text2 = """Hello, {}!\n\n Congratulations! You and {} just got a match. Here's there emailadress:
            {} \n \n we hope you have a pleasant collaboration. \n \n Tistacy""".format(matchinfo[0]["fullname"],\
            userinfo[0]["fullname"], matchinfo[0]["email"])
    message2 = 'Subject: {}\n\n{}'.format(subject, text2)

    server.login("tistacyhelpdesk@gmail.com", "webiktistacy")

    # Sends each message to the corresponding user
    server.sendmail("tistacyhelpdesk@gmail.com", userinfo[0]["email"], message1)
    server.sendmail("tistacyhelpdesk@gmail.com", matchinfo[0]["email"], message2)

    return True

def contacts(id):
    return db.execute("SELECT * FROM pairs WHERE id=:id", id=id)

def conversation(id, otherid):

    return db.execute("SELECT * FROM messages WHERE id=:id AND other_id=:otherid OR id=:otherid AND other_id=:id", \
                    id=id, otherid=otherid)

def chat(id,otherid,message):

    return db.execute("INSERT INTO messages (message, id, other_id) VALUES (:message, :id, :other_id)", \
                        message=message, id=id, other_id=otherid)


