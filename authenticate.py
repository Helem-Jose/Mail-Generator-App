import google.oauth2.credentials
import google_auth_oauthlib.flow
import flask
import json
from google.auth.transport.requests import Request
from db import db
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64
from models import User
from dotenv import load_dotenv

load_dotenv()

scopes = ['https://www.googleapis.com/auth/gmail.readonly',
                'https://www.googleapis.com/auth/gmail.modify']

redirect_uri = 'http://localhost:5000/oauth2callback'

def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json',
        scopes=scopes)

    flow.redirect_uri = redirect_uri

    authorization_url, state = flow.authorization_url(access_type='offline')

    return authorization_url, state


def callback(state, code):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('client_secret.json',
        scopes=scopes,
        state=state)

    flow.redirect_uri = redirect_uri
    authorization_response = flask.request.url
    print("Getting credentials...")
    flow.fetch_token(authorization_response=authorization_response, code=code)
    credentials = flow.credentials.to_json()
    
    return credentials

def fix_base64_padding(b64_string: str) -> str:
    return b64_string + '=' * (-len(b64_string) % 4)

# Encrypt a refresh token
def encrypt_token(token: str, Key: str) -> str:
    key = base64.urlsafe_b64decode(fix_base64_padding(Key))
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # 96-bit nonce
    ct = aesgcm.encrypt(nonce, token.encode(), None)
    return base64.urlsafe_b64encode(nonce + ct).decode()

# Decrypt a refresh token
def decrypt_token(encrypted_token: str, key_b64: str) -> str:
    # Fix padding and decode key
    key_padded = fix_base64_padding(key_b64)
    key = base64.urlsafe_b64decode(key_padded)

    # Fix padding and decode token
    token_padded = fix_base64_padding(encrypted_token)
    data = base64.urlsafe_b64decode(token_padded)

    nonce = data[:12]
    ct = data[12:]

    aesgcm = AESGCM(key)
    decrypted = aesgcm.decrypt(nonce, ct, None)

    return decrypted.decode()

def get_credentials(email):
    current_user = db.session.execute(db.select(User).where(User.email == email)).scalar()
    credentials = current_user.credentials
    if credentials == "NOT SET":
        return "NOT SET"
    else:
        credentials = decrypt_token(current_user.credentials, os.environ.get("encryption_key"))
        creds = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(credentials))
        if not creds:
            print("Invalid credentials in session")
            return None
        elif creds.expired and creds.refresh_token:
            print("Refreshing credentials from session...")
            creds.refresh(Request())
            print("Token refreshed successfully.")
            current_user.credentials = encrypt_token(creds.to_json(), os.environ.get("encryption_key"))
            db.session.commit()
        return creds.to_json()