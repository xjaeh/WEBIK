import random
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context
from flask_session import Session
import smtplib
import random
import string
from flask import Flask, flash, redirect, render_template, request, session, url_for

# Initializes database
db = SQL("sqlite:///WEBIK.db")


def register(username, hash, fullname, work, search, email, extra_search):
    """Register machanism"""

    # Initializez variables
    users = db.execute("SELECT * FROM users")
    usernames = [user["username"] for user in users]
    emails = [user["email"] for user in users]

    # Checkz if username and email already exists
    if username in usernames:
        return "error_user"
    elif email in emails:
        return "error_email"

    # Puts user information into the database
    else:
        try:
            server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)

            # Creates a seperate  email for each person
            subject = "Welcome"

            with open("email_templates/welcome.txt", "r") as mail:
                text = str(mail.read()).format(fullname)

            message = 'Subject: {}\n\n{}'.format(subject, text)

            server.login("collabstudiohelpdesk@gmail.com", "webikcollab")
            server.sendmail("collabstudiohelpdesk@gmail.com", email, message)

        # Returns an error in cade of unreachable email adress
        except:
            return "error_invalid_mail"

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
            return "error_fullname"

    # Checks if all the passwordfields are filled in otherwise apology
    if password or confirm_password or old_password:
        if not old_password or not password or not confirm_password:
            return "error_password"
        # Changes the password if the user submitted all passwords
        else:
            if password != confirm_password:
                return "error_password_confirmation"
            rows = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
            if pwd_context.verify(old_password, rows[0]["hash"]) == False:
                return "error_password_verify"
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

    db.execute("INSERT INTO pictures (id, picture) VALUES (:id, :picture)",\
                id=id, picture=filename)


def find(id):
    """Returns a potential match id"""

    # Selects search catogory from user and returns all users with the same work
    search = db.execute("SELECT search FROM users WHERE id=:id", id=id)
    extra_search = db.execute("SELECT extra_search FROM users WHERE id=:id", id=id)
    possible_matches = db.execute("SELECT id FROM users WHERE work=:search OR work=:extra_search", \
                                    search=search[0]["search"], \
                                    extra_search=extra_search[0]["extra_search"])
    possible_matches_set = set(match["id"] for match in possible_matches)

    # Selects all the users which are already seen by the user
    already_seen = db.execute("SELECT other_id FROM matchstatus WHERE id=:id", id=id)
    already_seen_set= set(already["other_id"] for already in already_seen)
    already_reject = db.execute("SELECT id FROM matchstatus WHERE other_id=:id AND status=:status", id=id, status="false")
    already_reject_set= set(already["id"] for already in already_reject)

    # Returns a user id from possible_matches minus the ones already seen
    show = possible_matches_set - already_seen_set - already_reject_set
    shows = [id for id in show]
    if shows == []:
        return 'empty'
    else:
        return random.choice(shows)


def find_work(id,finding):
    """Returns profession of user"""

    work = db.execute("SELECT work FROM users WHERE id=:id", id=finding)
    return work


def select(finding):
    """Returns all pictures from the users id"""

    picture = db.execute("SELECT * FROM pictures WHERE id=:id", id=finding)
    return picture


def delete(picture, id):
    """Lets the user remove a picture from the database"""

    return db.execute("DELETE FROM pictures WHERE picture=:picture", picture=picture)


def status_update(id,other_id,status):
    """Inserts status into database"""

    db.execute("INSERT INTO matchstatus (id, other_id, status) VALUES (:id, :other_id, :status)",\
                id=id, other_id=other_id, status=status)


def inform_match(id, other_id):
    """Sends new password to user and his/her match in case of a match"""

    # Selects user and match information
    user_info = db.execute("SELECT * FROM users WHERE id=:id", id=id)
    match_info = db.execute("SELECT * FROM users WHERE id=:id", id=other_id)

    # Sets up emailserver
    server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)

    # Creates a seperate  email for each person
    subject = "You got a match"

    # Opens new_password.txt as template and fills it in
    with open("email_templates/match.txt", "r") as mail:
        text_1 = str(mail.read()).format(user_info[0]["fullname"], \
                    match_info[0]["fullname"], match_info[0]["fullname"])
        text_2 = str(mail.read()).format(match_info[0]["fullname"], \
                    user_info[0]["fullname"], user_info[0]["fullname"])

    message_1 = 'Subject: {}\n\n{}'.format(subject, text_1)
    message_2 = 'Subject: {}\n\n{}'.format(subject, text_2)

    # log into emailaccount
    server.login("collabstudiohelpdesk@gmail.com", "webikcollab")

    # Sends each message to the corresponding user
    server.sendmail("collabstudiohelpdesk@gmail.com", user_info[0]["email"], message_1)
    server.sendmail("collabstudiohelpdesk@gmail.com", match_info[0]["email"], message_2)

    return True


def status_check(id, other_id):
    """Checks if two id's have a match"""

    # Selects the two statuses
    status_1 = db.execute("SELECT status FROM matchstatus WHERE id=:id and other_id=:other_id", \
                    id=id, other_id = other_id)
    status_2 = db.execute("SELECT status FROM matchstatus WHERE id=:other_id and other_id=:id", \
                    other_id = other_id, id=id)

    # Returns True or False depending upon mutual like or not
    if len(status_1) == 0 or len(status_2) == 0:
        return False
    elif status_1[0]["status"] == "true" or status_2[0]["status"] == "true":
        return True
    else:
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

            # Sets up server
            server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)

            # Creates a seperate  email for each person
            subject = "New Password"

            # Opens new_password.txt as template and fills it in
            with open("email_templates/new_password.txt", "r") as mail:
                text = str(mail.read()).format(username, password)

            # Sets up mail
            message = 'Subject: {}\n\n{}'.format(subject, text)

            # Sends mail
            server.login("collabstudiohelpdesk@gmail.com", "webikcollab")
            server.sendmail("collabstudiohelpdesk@gmail.com", email, message)


def contacts(id):
    """Loads all contacts from the pairs database"""

    return db.execute("SELECT * FROM pairs WHERE id=:id", id=id)


def conversation(id, other_id):
    """Loads all messages from the messages database between the two given id's"""

    return db.execute("""SELECT * FROM messages WHERE id=:id
                        AND other_id=:other_id OR id=:other_id AND other_id=:id""", \
                        id=id, other_id=other_id)


def chat(id,other_id,message):
    """Inserts a message with a to and from into the messages database"""

    return db.execute("""INSERT INTO messages (message, id, other_id)
                        VALUES (:message, :id, :other_id)""", \
                        message=message, id=id, other_id=other_id)


def pair(id, other_id):
    """Adds a new pair to the pairs database"""

    # stores information of both id's in seperate variables
    user1 = db.execute("SELECT * FROM users WHERE id=:id", id=id)
    user2 = db.execute("SELECT * FROM users WHERE id=:other_id", other_id=other_id)

    # Inserts a pair with id = user_1 and other_id = user_2
    db.execute("INSERT INTO pairs (id, username, other_id, other_username) VALUES \
            (:id, :username, :other_id, :other_username)", id=user1[0]["id"], \
            username=user1[0]["username"], other_id=user2[0]["id"], \
            other_username=user2[0]["username"])

    # Inserts a pair with id = user_2 and other_id = user_1
    db.execute("INSERT INTO pairs (id, username, other_id, other_username) VALUES \
<<<<<<< HEAD
            (:id, :username, :other_id, :other_username)", id=user2[0]["id"], \
            username=user2[0]["username"], other_id=user1[0]["id"], \
            other_username=user1[0]["username"])

    return True
=======
    (:id, :username, :other_id, :other_username)", id=user2[0]["id"], username=user2[0]["username"] \
    , other_id=user1[0]["id"], other_username=user1[0]["username"])
    return True
>>>>>>> be239514c1d58965c76f53600fc955b5599cabfd
