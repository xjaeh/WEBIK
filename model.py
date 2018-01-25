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

def register(username, hash, fullname, work, search, email):
    """Register machanism"""

    # Initialise variables
    users = db.execute("SELECT * FROM users")
    usernames = [user["username"] for user in users]
    emails = [user["email"] for user in users]

    # Checks if username and email already exists
    if username in usernames:
        return "x"
    elif email in emails:
        return "y"

    # Puts user information into the database
    else:
        db.execute("INSERT INTO users (username, hash, fullname, work, search, email) VALUES \
                   (:username, :hash, :fullname, :work, :search, :email)", username = username, \
                    hash = hash, fullname = fullname, work = work, search = search, email = email)

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

def account(fullname, oldpassword, password, confirmpassword, email, work, search):
    """Let's the user change his/her personal information"""

    # Changes users fullname if the user submitted one
    if fullname:
        if " " in fullname:
            db.execute("UPDATE users SET fullname = :fullname WHERE id = :id" , \
            fullname = fullname, id = session["user_id"], )
        else:
            return 0

    # Checks if all the passwordfields are filled in otherwise apology
    if password or confirmpassword or oldpassword:
        if not oldpassword or not password or not confirmpassword:
            return 1
        # Changes the password if the user submitted all passwords
        else:
            if password != confirmpassword:
                return 3
            rows = db.execute("SELECT * FROM users WHERE id=:id", id= session["user_id"])
            if pwd_context.verify(oldpassword, rows[0]["hash"]) == False:
                return 1
            else:
                db.execute("UPDATE users SET hash = :hash WHERE id = :id" , \
                    hash = pwd_context.hash(password), id = session["user_id"], )

    # Changes the users email if the user submitted one
    if email:
        db.execute("UPDATE users SET email = :email WHERE id = :id" , \
        email = email, id = session["user_id"], )

    # Changes the users profession is the user submitted one
    if work and work != "I am a ...":
        db.execute("UPDATE users SET work = :work WHERE id = :id" , \
        work = work, id = session["user_id"], )

    # Changes the users search if the user submitted one
    if search and search != "I am looking for a ...":
        db.execute("UPDATE users SET search = :search WHERE id = :id" , \
        search = search, id = session["user_id"], )

def profile(id):
    """Returns all photos under the users id in reverse order"""
    photos = db.execute("SELECT picture FROM pictures WHERE id=:id", id=id)
    return photos[::1]

def upload(filename, id):
    """Lets the user upload a new photo and adds it to the database"""
    db.execute("INSERT INTO pictures (id, picture) VALUES (:id, :picture)", id=id, picture=filename)

def find(id):
    """Returns a potential match id"""

    # Selects search catogory from user and returns all users with the same work
    search = db.execute("SELECT search FROM users WHERE id=:id", id=id)
    possible_matches = db.execute("SELECT id FROM users WHERE work=:search", search=search[0]["search"])
    possible_matchesset = set(match["id"] for match in possible_matches)

    # Selects all the users which are already seen by the user
    alreadyseen= db.execute("SELECT otherid FROM matchstatus WHERE id=:id", id=id)
    alreadyseenset= set(already["otherid"] for already in alreadyseen)

    # Returns a user id from possible_matches minus the ones already seen
    show = possible_matchesset - alreadyseenset
    shows = [id for id in show]
    if shows == []:
        return 'empty'
    else:
        return random.choice(shows)

def select(id):
    """Returns all pictures from the users id"""
    picture = db.execute("SELECT * FROM pictures WHERE id=:id", id=id )
    return picture

def delete(picture, id):
    """Lets the user remove a picture from the database"""
    return db.execute("DELETE FROM pictures WHERE picture = :picture", picture = picture)

def statusupdate(id,otherid,status):
    """Inserst status into database"""
    db.execute("INSERT INTO matchstatus (id, otherid, status) VALUES (:id, :otherid, :status)", id=id, otherid=otherid, status=status)

def statuscheck(id, otherid):
    """Checks if two id's have a match"""

    # Selects the two statuses
    status1 = db.execute("SELECT status FROM matchstatus WHERE id=:id and otherid=:otherid", id=id, otherid=otherid)
    status2 = db.execute("SELECT status FROM matchstatus WHERE id=:id and otherid=:otherid", id=otherid, otherid=id)

    # Returns True or False depending upon mutual like or not
    try:
        status1[0]["status"] == "true" and status2[0]["status"] == "true"
        return True
    except:
        return False

def password_generator(chars=string.ascii_uppercase + string.digits):
    """Generate a random password with length 10"""
    return ''.join(random.choice(chars) for i in range(10))

def retrievepassword(username, email):
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
            db.execute("UPDATE users SET hash =:hash WHERE username =:username" , \
                    hash = pwd_context.hash(password), username = username, )

            # Sends new password to user and sets email structure
            server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)
            subject = "Forgot password"
            text = "Hello, {}!\n\n your new password is: \n\n '{}' \n\n you can now use this password to log into your account. \n don't forget to change youer password after logging in.".format(rows[0]["fullname"], password)
            message = 'Subject: {}\n\n{}'.format(subject, text)

        # Sets up emailaccount
        server.login("tistacyhelpdesk@gmail.com", "webiktistacy")
        server.sendmail("tistacyhelpdesk@gmail.com", email, message)

def inform_match(id1, id2):
    """Sends new password to user and his/her match in case of a match"""

    # Selects user and match information
    userinfo = db.execute("SELECT * FROM users WHERE id=:id", id=id1)
    matchinfo = db.execute("SELECT * FROM users WHERE id=:id", id=id2)

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

