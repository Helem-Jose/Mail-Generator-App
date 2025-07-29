from flask import Flask, render_template, redirect, url_for, jsonify
from flask import request, session
from flask_sqlalchemy import SQLAlchemy
from google.oauth2.credentials import Credentials
from db import init_app, db
from models import User
import re
import requests
import authenticate
import get_messages
import json
import threading
import agent

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
        return render_template("home.html")

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
    session['style_hint'] = """
Connective word usage is 4.0%, indicating a low presence of linking words.
Pronoun usage is 8.0%, which is considered moderate.
Lexical diversity (based on unique words longer than 3 characters) is 65.0%, suggesting a very high variety in vocabulary.
The average sentence length is 15.2 words, which is considered long.
Clause density (indicating structural complexity from subordinate, adverbial, or relative clauses) is 12.0%, which is a moderate level.
Passive voice usage is 3.0%, indicating a low preference for passive constructions.
The average word length is 4.8 characters, which is considered short.
The average number of syllables per word is 1.5, indicating short word complexity.
The Type-Token Ratio (vocabulary richness) is 55.0%, suggesting a very high diversity in word choice.
Informal language usage is 0.5%, indicating a very low presence of informal words.
The Flesch-Kincaid readability grade is 7.5, meaning the text is easy to read (suitable for middle school grades).
The SMOG readability index is 9.0, suggesting the text is easy to read.
The Gunning-Fog readability score is 9.8, indicating the text is moderately easy to read (suitable for high school grades).
The proportion of nouns is 22.0%, which is a high ratio of nouns in the text.
The proportion of verbs is 18.0%, which is a high ratio of verbs in the text.
The proportion of adjectives is 7.0%, which is a moderate ratio of adjectives in the text.
The proportion of adverbs is 5.0%, which is a moderate ratio of adverbs in the text.
Contraction usage is 1.0%, indicating a very low presence of contractions.
Contraction usage is 1.0%, indicating a very low presence of contractions.
Exclamation mark usage is 0.2%, which is a very low density per sentence.
Question mark usage is 0.8%, which is a very low density per sentence.
Emoji or special symbol usage is 0.0%, indicating a very low presence of such characters.
""" #Properly generate this and put in database
    session['summary'] = convert_summary_to_html(agent.summarize_threads(get_mail_thread(session["mails"])).split("**Summary:**")[1])
    print("Summary Generated : ", session['summary'])
    question_dict = agent.run_email_assistant(session['summary'], session["style_hint"], session['name'], session["additional_info"])
    print("Received questions", question_dict)
    reply = "Gathering info..."
    if question_dict != "FINAL ANSWER":
        for i, question in question_dict.items():
            session['questions'].append(question)
        next_question = session['questions'][0] 
    else:
        reply = agent.generate_email_reply(session['summary'], session["style_hint"], session["additional_info"])
    session.modified = True        

    return render_template("generate_mail.html", mails=session["mails"], summary=session['summary'], question = next_question, reply = reply)

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
    app.run(debug=True, threaded=True, use_reloader=False)
    #session.clear()  # Clear session at startup to avoid stale data