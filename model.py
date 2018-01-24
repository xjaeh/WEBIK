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
    return rows[0]["id"]

def login(username, hash):

    rows = db.execute("SELECT * FROM users WHERE username=:username", username=username)
    if len(rows) != 1 or not pwd_context.verify(hash, rows[0]["hash"]):
        return False
    else:
        return rows[0]["id"]

def account(fullname, password, email, work, search):
    # let's the user change it's personal information

    # changes users full name if the user submitted one
    if fullname:
        db.execute("UPDATE users SET fullname = :fullname WHERE id = :id" , \
        fullname = fullname, id = id, )

    # changes the password if the user submitted one
    if password:
        #v changes the users full name in the database
        db.execute("UPDATE users SET hash = :hash WHERE id = :id" , \
        hash = pwd_context.hash(password), id=id, )

    # changes the users email if the user submitted one
    if email:
        db.execute("UPDATE users SET email = :email WHERE id = :id" , \
        email = email, id = id, )

     # changes the users profession is the user submitted one
    if work:
        db.execute("UPDATE users SET work = :work WHERE id = :id" , \
        work = work, id = id, )

    if search:
        db.execute("UPDATE users SET search = :searcg WHERE id = :id" , \
        search = search, id = id, )
    """
    Functie: profile(id):
    	returned Profile of None
    Beschrijving: bewerken van profiel zoals plaatsen van foto’s en profielfoto wijzigen.

    """
def profile(id):
    # if user submits a new profilepicture, update profile pic

    # if user submits a photo (or multiple) add picture to users row in the database

    return db.execute("SELECT picture FROM pictures WHERE id=:id", id=id)

def upload(filename, id):

    db.execute("INSERT INTO pictures (id, picture) VALUES (:id, :picture)", id=id, picture=filename)

def find(id):
    rows = db.execute("SELECT * FROM users WHERE id=:id", id=id)
    search = rows[0]["search"]
    possible_matches = db.execute("SELECT * FROM users WHERE work=:search", search=search)

def select(id):

    rows = db.execute("SELECT * FROM pictures WHERE id=:id", id=id )
    return rows

def delete(picture, id):

    return db.execute("DELETE FROM pictures WHERE picture = :picture", picture = picture)

