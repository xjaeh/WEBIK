import random
from cs50 import SQL
from passlib.apps import custom_app_context as pwd_context
from flask_session import Session
from flask import Flask, flash, redirect, render_template, request, session, url_for
db = SQL("sqlite:///WEBIK.db")


def register(username, hash, fullname, work, search, email):

    users = db.execute("SELECT * FROM users")
    usernames = [user["username"] for user in users]
    emails = [user["email"] for user in users]

    if username in usernames:
        return 1
    if email in emails:
        return 2

    inserting = db.execute("INSERT INTO users (username, hash, fullname, work, search, email) VALUES \
                            (:username, :hash, :fullname, :work, :search, :email)", username = username, \
                            hash = hash, fullname = fullname, work = work, search = search, email = email)

    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    id = rows[0]["id"]
    return rows[0]["id"]

def login(username, hash):

    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    if len(rows) != 1 or not pwd_context.verify(hash, rows[0]["hash"]):
        return False
    else:
        return rows[0]["id"]

def account(fullname, password, email, work, search):
    # let's the user change his/her personal information

    # changes users full name if the user submitted one
    if fullname:
        db.execute("UPDATE users SET fullname = :fullname WHERE id = :id" , \
        fullname = fullname, id = session["user_id"], )

    # changes the password if the user submitted a valid oldpassword, and a new password and a passwordconfirmation
    if password or confirmpassword or oldpassword:
        if not oldpassword or not password or not confirmpassword:
            return 0
        else:
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
    if work:
        db.execute("UPDATE users SET work = :work WHERE id = :id" , \
        work = work, id = session["user_id"], )

    # changes the users _____ if the user submitted one
    if search:
        db.execute("UPDATE users SET search = :search WHERE id = :id" , \
        search = search, id = session["user_id"], )

def profile(id):
    # if user submits a new profilepicture, update profile pic

    # if user submits a photo (or multiple) add picture to users row in the database

    return db.execute("SELECT picture FROM pictures WHERE id=:id", id=id)

def upload(filename, id):

    db.execute("INSERT INTO pictures (id, picture) VALUES (:id, :picture)", id=id, picture=filename)

def find(id):
    search = db.execute("SELECT search FROM users WHERE id=:id", id=id)
    possible_matches = db.execute("SELECT id FROM users WHERE work=:search", search=search[0]["search"])
    possible_matchesset = set(match["id"] for match in possible_matches)
    alreadyseen= db.execute("SELECT otherid FROM matchstatus WHERE id=:id", id=id)
    alreadyseenset= set(already["otherid"] for already in alreadyseen)
    show = possible_matchesset - alreadyseenset
    shows = [id for id in show]
    if shows == []:
        return 'empty'
    else:
        return random.choice(shows)

def select(id):

    rows = db.execute("SELECT * FROM pictures WHERE id=:id", id=id )
    return rows

def delete(picture, id):

    return db.execute("DELETE FROM pictures WHERE picture = :picture", picture = picture)

def statusupdate(id,otherid,status):
    db.execute("INSERT INTO matchstatus (id, otherid, status) VALUES (:id, :otherid, :status)", id=id, otherid=otherid, status=status)

def statuscheck(id, otherid):
    option1 = db.execute("SELECT status FROM matchstatus WHERE id=:id and otherid=:otherid", id=id, otherid=otherid)
    option2 = db.execute("SELECT status FROM matchstatus WHERE id=:id and otherid=:otherid", id=otherid, otherid=id)
    if option1 == "true" and option2 == "true":
        return True

