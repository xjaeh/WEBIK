
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
    # if user submits a new profilepicture:
        db.execute("UPDATE users SET profilepicture = :profilepicture WHERE id = :id" , \
        profilepicture = request.form.get("profilepicture"), id = session["user_id"])
