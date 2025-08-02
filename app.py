from flask import Flask, render_template, redirect, url_for, jsonify
from flask import request, session
from flask_sqlalchemy import SQLAlchemy
from google.oauth2.credentials import Credentials
from db import init_app, db
from models import User
import re
import authenticate
import get_messages
import json
import os
import agent
from dotenv import load_dotenv
import bcrypt

load_dotenv()

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
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user = db.session.execute(db.select(User).where(User.email == email))
        current_user = user.scalar()
        if(current_user is None or not bcrypt.checkpw(password.encode('utf-8'), current_user.password.encode("utf-8"))):
            print("Invalid credentials")
            return render_template("login.html", session=True, message="Invalid credentials!")
        print("Valid credentials")
        session["email"] = email
        session["name"] =  current_user.name
        session["logged_in"] = True
        session["user_id"] = current_user.id
        return redirect(url_for('home'))

@app.route("/get_style")
def get_writingStyle():
    credentials = Credentials.from_authorized_user_info(json.loads(authenticate.get_credentials(session["email"])))
    messages = get_messages.get_full_messages(credentials, ["SENT"])
    final_thread = ""
    for message in messages:
        final_thread += message["body"]
    print("Final Thread :", final_thread,"\n")
    print("Fetching Users Writing style ...")
    writing_style = agent.get_style(final_thread)
    print("Writing Style :", "\n".join(writing_style), "\n")
    current_user = db.session.execute(db.select(User).where(User.email == session["email"])).scalar()
    current_user.writingStyle = "\n".join(writing_style)
    db.session.commit()
    return jsonify({"status": 200})

@app.route("/addUser", methods=["POST"])
def addUser():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        print(f"Hashed : {hashed}, Password:{password}")
        existing_user = db.session.execute(db.select(User).where(User.email == email))
        if len(existing_user.all()) != 0:
            return render_template("login.html", session=False, message="User already exists!")
        else:
            new_user = User(name=name, email=email, password=hashed.decode('utf-8'), credentials = "NOT SET", writingStyle = "NOT SET")
            db.session.add(new_user)
            db.session.commit()
        return render_template("login.html",session = True, message="User added successfully!")  

@app.route("/search", methods=["GET"])
def search_mails():
    if request.method == "GET":
        print("Searching emails...")
        query = f"subject:{request.args.get('subject')}"
        credentials = Credentials.from_authorized_user_info(json.loads(authenticate.get_credentials(session["email"])))
        if not credentials:
            print("No valid credentials found in session, redirecting to authorization...")
            return redirect(url_for('authorization'))
        print("Getting messages with query:", query)
        messages = get_messages.get_messages(credentials, query,)
        return jsonify({"results": messages})

@app.route("/search_window")
def search_window():
    current_user = db.session.execute(db.select(User).where(User.email == session["email"])).scalar()
    if current_user.writingStyle == "NOT SET":
        return redirect(url_for("writingStyle"))
    session['style_hint'] = current_user.writingStyle
    return render_template("search.html", username = session['name'], mailID = session['email'])

@app.route("/style")
def writingStyle():
    return render_template("writing_style.html")

@app.route("/get_thread/<threadID>", methods=["GET"])
def get_thread(threadID):
    print(f"Getting thread with thread ID : {threadID}")
    credentials = Credentials.from_authorized_user_info(json.loads(authenticate.get_credentials(session["email"])))
    if not credentials:
        print("No valid credentials found in session, redirecting to authorization...")
        return redirect(url_for('authorization'))
    mails = get_messages.get_thread(credentials, threadID)
    current_user = db.session.execute(db.select(User).where(User.email == session["email"])).scalar()
    current_user.mails = mails
    db.session.commit()
    return redirect(url_for("generate"))

@app.route("/get_model_output/<reply>", methods = ["GET"])
def question(reply):
    print("=====================\nQuestions Present till now: ", session['questions'], "\nAnswers :", session['answers'])
    print("Reply Received from user :", reply)
    next_question = ''
    if 'questions' in session:
        print("\nGenerating ..")
        session['answers'][session['questions'][0]] = reply
        print(session['answers'])
        session['questions'].pop(0)
        session.modified = True
        print("After removing element..", session['questions'], len(session['questions']))
        if len(session['questions']) == 0:
            print("Getting new questions ...")
            formatted = "\n".join([f"{qid}: {ans}" for qid, ans in session['answers'].items()])
            session["answers"] = {}
            print(formatted)
            session['additional_info'] += f"\n{formatted}"
            print("Additional info :", session['additional_info'])
            question_dict = agent.run_email_assistant(session['summary'], session["style_hint"], session['name'], session["additional_info"])
            print("Received questions", question_dict)
            if question_dict != "FINAL ANSWER":
                for i, question in question_dict.items():
                    session['questions'].append(question)
                session.modified = True
            else:
                reply = agent.generate_email_reply(session['summary'], session["style_hint"], session["additional_info"])
                print("*************\nReply generated :\n", re.sub(r"^FINAL ANSWER:\s*", "", reply))
                return jsonify({'reply': re.sub(r"^FINAL ANSWER:\s*", "", reply), 'question': "Reply generated..."})
        next_question = session['questions'][0] 
    else:
        print("Error")
    print("Session questions after loop :", session['questions'], len(session['questions']), "\n\n")
    session.modified = True
    return jsonify({'question':next_question})


def convert_summary_to_html(summary_text):
    lines = summary_text.strip().split('\n')
    list_items = [re.sub(r'^\*\s*', '', line) for line in lines if line.strip().startswith("*")]
    html = "<ul>\n" + "\n".join([f"<li>{item}</li>" for item in list_items]) + "\n</ul>"
    return html

@app.route("/generate_mail/", methods=["GET"])
def generate():
    session['additional_info'] = ''
    session['questions'] = []
    session['answers'] = {}
    current_user = db.session.execute(db.select(User).where(User.email == session["email"])).scalar()
    mails = current_user.mails
    session['summary'] = convert_summary_to_html(agent.summarize_threads(get_mail_thread(mails)).split("**Summary:**")[1])
    print("Summary Generated : ", session['summary'])
    question_dict = agent.run_email_assistant(session['summary'], session["style_hint"], session['name'], session["additional_info"])
    print("Received questions", question_dict)
    reply = "Gathering info..."
    next_question = "Generated mail.."
    if question_dict != "FINAL ANSWER":
        for i, question in question_dict.items():
            session['questions'].append(question)
        next_question = session['questions'][0] 
    else:
        reply = agent.generate_email_reply(session['summary'], session["style_hint"], session["additional_info"])
    session.modified = True        

    return render_template("generate_mail.html", mails=mails, summary=session['summary'], question = next_question, reply = reply)

def get_mail_thread(mails):
    thread = ""
    for mail in mails:
        thread += f"From: {mail['SenderName']} \nSubject: {mail['subject']}\n{mail['body']}\n\n"
    return thread

@app.route("/home")
def home():
    print("Accessing home page...")
    if "logged_in" not in session or not session["logged_in"]:
        print("User not logged in, redirecting to login...")
        return render_template("login.html", session=True, message="Please log in first!")
    credentials = authenticate.get_credentials(session["email"])
    print("Credentials Stored :", credentials)
    if credentials == "NOT SET":
        print("No valid credentials found in session, redirecting to authorization...")
        return redirect(url_for('authorization'))
    else:
        session['credentials'] = credentials
            
    return redirect(url_for('search_window'))

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

@app.route("/logout")
def logout():
    session.clear()
    session['logged_in'] = False
    print("Logging out...")
    return redirect(url_for("startup"))

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
    current_user = db.session.execute(db.select(User).where(User.email == session['email'])).scalar()
    current_user.credentials = authenticate.encrypt_token(credentials, os.environ.get("encryption_key"))
    db.session.commit()
    session["credentials"] = credentials
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, threaded=True, use_reloader=False)
    session.clear()
