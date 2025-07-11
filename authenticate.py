import google.oauth2.credentials
import google_auth_oauthlib.flow
import flask

scopes = ['https://www.googleapis.com/auth/gmail.addons.current.action.compose',
                'https://www.googleapis.com/auth/gmail.addons.current.message.action']

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
    flow.fetch_token(authorization_response=authorization_response, code=code)
    credentials = credentials_to_dict(flow.credentials)

    return credentials

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'granted_scopes': credentials.granted_scopes}