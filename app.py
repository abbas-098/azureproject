from flask import Flask, render_template, redirect, request, session,flash
from flask_session import Session
from help import apology, login_required
import pyodbc
import pandas as pd
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Configures the application
app = Flask(__name__)

# Ensure responses aren't cached
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

# Configuring database connection
server = 'teamazure098.database.windows.net'
database = 'team-azure-python-project'
username = 'abbas'
password = 'P@ssword098'
driver = '{ODBC Driver 17 for SQL Server}'
conn = pyodbc.connect('DRIVER=' + driver + ';SERVER=' + server + ';PORT=1433;DATABASE=' + database + ';UID=' + username + ';PWD=' + password)


# defining the login page
@app.route("/login", methods = ["GET", "POST"])
def login():

    # Clear any previous user_id
    session.clear()

    # anyone reach route via POST (by form)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Thief! Provide a username ")

        # Ensure password is submitted
        elif not request.form.get("password"):
            return apology("My Precious! You must provide password")

        try:
            # Query the azure database for the username
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username = ?", request.form.get("username"))
            rows = cursor.fetchall()
        except:
            return apology("Login feature not working")
        else:
            for row in rows:
                # ensure the username exists and password is correct
                if len(row) < 3 or not check_password_hash(row.hash, request.form.get("password")):
                    return apology("invalid username and/or password")
                else:
                    # Remember which user is logged in
                    session["user_id"] = row.user_id
                    conn.commit()
                    # redirect to home page once logged in
                    flash("Logged In")
                    return redirect("/")
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    flash("Logged Out")
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
 
    if request.method == "POST":

       # ensure a username is entered
        if not request.form.get("username"):
           return apology("Thief! Provide a username ")

        # ensure password and password confirmation is entered
        elif not request.form.get("password") or not request.form.get("confirmation"):
            return apology("My Precious! You must provide password")

        # ensuring the passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Smeagol says passwords don't match")

        # Hashing the password
        hash = generate_password_hash(request.form.get("password"))

        try:
            #insert the username and hash password into database.
            cursor = conn.cursor()
            rows = cursor.execute("""INSERT INTO Users (username,hash) VALUES (?,?) """, request.form.get("username"), hash)
            conn.commit()
            print("Success")
        except:
            return apology("username is already registered")
        else:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users WHERE username = ? ", request.form.get("username"))
            rows = cursor.fetchall()
            for row in rows:
                # remembering which user is logged in
                session["user_id"] = row.user_id
                print("found ID")
                conn.commit()
                # redirect
                flash("Registered!")
                return redirect("/")
    # else if reached by GET then redirect to the register page
    else:
        return render_template("register.html")

@app.route("/")
@login_required
def index():
    "Shows the main page"
    # selecting all the data
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM MergedTable")
    rows = cursor.fetchall()
    return render_template("table.html", rows = rows)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run(debug =True)