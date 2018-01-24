from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context
from flask_session import Session
import smtplib
import random
import string
from flask import Flask, flash, redirect, render_template, request, session, url_for
db = SQL("sqlite:///WEBIK.db")

def register(username, hash, fullname, work, search, email):

    users = db.execute("SELECT * FROM users")
    usernames = [user["username"] for user in users]
    emails = [user["email"] for user in users]

    if username in usernames:
        return x
    elif email in emails:
        return y
    else:
        db.execute("INSERT INTO users (username, hash, fullname, work, search, email) VALUES \
                   (:username, :hash, :fullname, :work, :search, :email)", username = username, \
                    hash = hash, fullname = fullname, work = work, search = search, email = email)

    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    return rows[0]["id"]

def login(username, hash):

    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    if len(rows) != 1 or not pwd_context.verify(hash, rows[0]["hash"]):
        return False
    else:
        return rows[0]["id"]

def account(fullname, oldpassword, password, confirmpassword, email, work, search):
   # let's the user change his/her personal information

    # changes users full name if the user submitted one
    if fullname:
        if " " in fullname:
            db.execute("UPDATE users SET fullname = :fullname WHERE id = :id" , \
            fullname = fullname, id = session["user_id"], )
        else:
            return 0

    # changes the password if the user submitted a valid oldpassword, and a new password and a passwordconfirmation
    if password or confirmpassword or oldpassword:
        if not oldpassword or not password or not confirmpassword:
            return 1
        else:
            if password != confirmpassword:
                return 3
            rows = db.execute("SELECT * FROM users WHERE id=:id", id= session["user_id"])
            if pwd_context.verify(oldpassword, rows[0]["hash"]) == False:
                return 1
            else:
                db.execute("UPDATE users SET hash = :hash WHERE id = :id" , \
                    hash = pwd_context.hash(password), id = session["user_id"], )

    # changes the users email if the user submitted one
    if email:
        db.execute("UPDATE users SET email = :email WHERE id = :id" , \
        email = email, id = session["user_id"], )

     # changes the users profession is the user submitted one
    if work and work != "I am a ...":
        db.execute("UPDATE users SET work = :work WHERE id = :id" , \
        work = work, id = session["user_id"], )

    # changes the users _____ if the user submitted one
    if search and search != "I am looking for a ...":
        db.execute("UPDATE users SET search = :search WHERE id = :id" , \
        search = search, id = session["user_id"], )

def profile(id):
    # returns all photos under the users id in reverse order
    photos = db.execute("SELECT picture FROM pictures WHERE id=:id", id=id)
    return photos[::1]

def upload(filename, id):
    # lets the user upload a new photo and adds it to the database
    db.execute("INSERT INTO pictures (id, picture) VALUES (:id, :picture)", id=id, picture=filename)

def find(id):
    rows = db.execute("SELECT * FROM users WHERE id=:id", id=id)
    search = rows[0]["search"]
    possible_matches = db.execute("SELECT * FROM users WHERE work=:search", search=search)

def select(id):
    # returns all pictures under a users id
    picture = db.execute("SELECT * FROM pictures WHERE id=:id", id=id )
    return picture

def delete(picture, id):
    # lets the user remove a picture from the database
    return db.execute("DELETE FROM pictures WHERE picture = :picture", picture = picture)

def password_generator(chars=string.ascii_uppercase + string.digits):
    # generate a random password with length 10, containing capital letters and numbers
    return ''.join(random.choice(chars) for i in range(10))

def retrievepassword(username, email):
    # allows the user to have a new password sent to them
    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    if not rows:
         return 0
    else:
        if email != rows[0]["email"]:
            return 1
        else:
            # generates a new password
            password = password_generator()

            # changes password in database
            db.execute("UPDATE users SET hash =:hash WHERE username =:username" , \
                    hash = pwd_context.hash(password), username = username, )

            # sends new password to user
            server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)

            subject = "Forgot password"
            text = "Hello, {}!\n\n your new password is: \n\n '{}' \n\n you can now use this password to log into your account. \n don't forget to change youer password after logging in.".format(rows[0]["fullname"], password)
            message = 'Subject: {}\n\n{}'.format(subject, text)

        server.login("tistacyhelpdesk@gmail.com", "webiktistacy")
        server.sendmail("tistacyhelpdesk@gmail.com", email, message)

def inform_match(id1, id2):
     # sends new password to user and his/her match in case of a match
    userinfo = db.execute("SELECT * FROM users WHERE id=:id", id=id1)
    matchinfo = db.execute("SELECT * FROM users WHERE id=:id", id=id2)

    server = smtplib.SMTP_SSL('smtp.googlemail.com', 465)

    subject = "You got a match"

    # creates a seperate user for each person
    text1 = "Hello, {}!\n\n Congratulations! You and {} just got a match. Here's there emailadress: {} \n \n we hope you have a pleasant collaboration. \n \n Tistacy".format(matchinfo[0]["fullname"], \
        userinfo[0]["fullname"], userinfo["email"])
    message1 = 'Subject: {}\n\n{}'.format(subject, text1)

    text2 = "Hello, {}!\n\n Congratulations! You and {} just got a match. Here's there emailadress: {} \n \n we hope you have a pleasant collaboration. \n \n Tistacy".format(userinfo[0]["fullname"], \
        matchinfoinfo[0]["fullname"], matchinfo["email"])
    message2 = 'Subject: {}\n\n{}'.format(subject, text2)

    server.login("tistacyhelpdesk@gmail.com", "webiktistacy")

    # sends each message to the corresponding user
    server.sendmail("tistacyhelpdesk@gmail.com", userinfo[0]["email"], message1)
    server.sendmail("tistacyhelpdesk@gmail.com", matchinfo[0]["email"], message2)

    return True
