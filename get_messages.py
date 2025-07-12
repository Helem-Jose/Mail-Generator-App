from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
 
def get_messages(creds):
    print("Getting details...")
    creds = Credentials.from_authorized_user_info(creds)
    if not creds or not creds.valid:
        print("Invalid credentials")
        return []
    try:
        service = build('gmail', 'v1', credentials=creds)
        collection = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=10)
        response = collection.execute()
        print("Response:", response)
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None