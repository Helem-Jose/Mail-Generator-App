from flask import Flask, render_template, redirect, url_for
from flask import request, session
from flask_sqlalchemy import SQLAlchemy
from db import init_app, db
from models import User
import authenticate

app = Flask(__name__)
app.secret_key = "12344o3o_kekien_l9123ldfk**34mj"
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

@app.route("/home")
def home():
    if "logged_in" not in session or not session["logged_in"]:
        return render_template("login.html", session=True, message="Please log in first!")
    return render_template("home.html", session=True, name=session.get("name", "Guest"))

@app.route("/authorize")
def authorization():
    print("Authorizing...")
    authorization_url, state = authenticate.authorize()
    session['state'] = state
    return redirect(authorization_url)

@app.route("/oauth2callback")
def oauth2callback():
    credientials = authenticate.callback(session['state'], request.args.get('code'))
    session['credentials'] = credientials
    session['logged_in'] = True
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
    