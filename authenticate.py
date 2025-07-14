import google.oauth2.credentials
import google_auth_oauthlib.flow
import flask
import json
from google.auth.transport.requests import Request

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


def get_credentials_from_session(session):
    if 'credentials' in session:
        credentials = session['credentials']
        creds = google.oauth2.credentials.Credentials.from_authorized_user_info(json.loads(credentials))
        if not creds:
            print("Invalid credentials in session")
            return None
        elif creds.expired and creds.refresh_token:
            print("Refreshing credentials from session...")
            creds.refresh(Request())
            print("Token refreshed successfully.")
            session['credentials'] = creds.to_json()
        return creds
    else:
        print("No credentials found in session")
        return None