from flask import Flask, render_template, redirect, url_for, jsonify
from flask import request, session
from flask_sqlalchemy import SQLAlchemy
from google.oauth2.credentials import Credentials
from db import init_app, db
from models import User
import requests
import authenticate
import get_messages
import json
import threading

with open("app_secret_key.json", "r") as f:
    secret_key = json.load(f)["app-key"]

app = Flask(__name__)
app.secret_key = secret_key
init_app(app)

@app.route("/")
def index():
    return "<h1>Hello World!</h1>"

@app.route("/login")
def startup():
    return render_template("login.html", session=True)

@app.route("/validateUser", methods=["POST"])
def validate_user():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.session.execute(db.select(User).where(User.email == email, User.password == password))
        current_user = user.scalar()
        if(current_user is None):
            print("Invalid credentials")
            return render_template("login.html", session=True, message="Invalid credentials!")
        print("Valid credentials")
        session["email"] = email
        session["name"] =  current_user.name
        session["logged_in"] = True
        session["user_id"] = current_user.id
        return render_template("login.html", session = True, message="Login successful!")

@app.route("/addUser", methods=["POST"])
def addUser():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        existing_user = db.session.execute(db.select(User).where(User.email == email))
        if len(existing_user.all()) != 0:
            return render_template("login.html", session=False, message="User already exists!")
        else:
            new_user = User(name=name, email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
        return render_template("login.html",session = True, message="User added successfully!")  

@app.route("/search", methods=["GET"])
def search_mails():
    if request.method == "GET":
        print("Searching emails...")
        query = f"subject:{request.args.get('subject')}"
        credentials = authenticate.get_credentials_from_session(session)
        if not credentials:
            print("No valid credentials found in session, redirecting to authorization...")
            return redirect(url_for('authorization'))
        print("Getting messages with query:", query)
        messages = get_messages.get_messages(credentials, query,)
        return jsonify({"results": messages})

@app.route("/search_window")
def search_window():
    return render_template("search.html")

@app.route("/get_thread/<threadID>", methods=["GET"])
def get_thread(threadID):
    print(f"Getting thread with thread ID : {threadID}")
    credentials = authenticate.get_credentials_from_session(session)
    if not credentials:
        print("No valid credentials found in session, redirecting to authorization...")
        return redirect(url_for('authorization'))
    mails = get_messages.get_thread(credentials, threadID)
    session["mails"] = mails
    return redirect(url_for("generate"))

@app.route("/generate_mail/", methods=["GET"])
def generate():
    return render_template("generate_mail.html", mails=session["mails"])

@app.route("/home")
def home():
    print("Accessing home page...")
    if "logged_in" not in session or not session["logged_in"]:
        print("User not logged in, redirecting to login...")
        return render_template("login.html", session=True, message="Please log in first!")
    if "credentials" in session:
        credentials = authenticate.get_credentials_from_session(session)
        if not credentials:
            print("No valid credentials found in session, redirecting to authorization...")
            return redirect(url_for('authorization'))
    return render_template("home.html", session=True, name=session.get("name", "Guest"))

@app.route("/authorize")
def authorization():
    print("Authorizing...")
    if "credentials" in session:
        creds = Credentials.from_authorized_user_info(json.loads(session["credentials"]))
        if creds and creds.valid and creds.expired == False and creds.refresh_token:
            print("Already authorized, redirecting to home...")
            print("Credentials:", session["credentials"])
            return redirect(url_for('home'))
    authorization_url, state = authenticate.authorize()
    session['state'] = state
    session.modified = True
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    print("OAuth2 callback...")
    if request.args.get('state') != session['state']:
        print("State mismatch. Possible CSRF attack.")
        return redirect(url_for('authorization'))
    credentials = authenticate.callback(session['state'], request.args.get('code'))
    session['credentials'] = credentials
    print("Credentials received:", credentials)
    creds = Credentials.from_authorized_user_info(json.loads(credentials))
    if not creds.refresh_token:
        print("Refresh token not present. Re-authorizing...")
        return redirect(url_for('authorization'))
    print("Credentials validity check...",  creds.valid)
    session['logged_in'] = True
    return redirect(url_for('home'))

if __name__ == "__main__":
    # use_reloader=False to prevent the app from running twice may help in session issues
    app.run(debug=True, threaded=True)
    #session.clear()  # Clear session at startup to avoid stale data
    