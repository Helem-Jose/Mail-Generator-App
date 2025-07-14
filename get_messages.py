from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from base64 import urlsafe_b64decode as decode_base64url
 
def get_messages(creds, query):
    print("Getting messages...")
    if not creds or not creds.valid:
        print("Invalid credentials")
        return []
    try:
        service = build('gmail', 'v1', credentials=creds)
        collection = service.users().messages().list(userId='me', q = query, maxResults=10)
        response = collection.execute()
        if 'messages' not in response:
            print("No messages found.")
            return []
        ans = []
        for message in response['messages']:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            id = msg['id']
            thread_id = msg['threadId']
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            body = msg.get('snippet', '(No Body)')
            ans.append({
                'id': id,
                'threadId': thread_id,
                'subject': subject,
                'body': body
            })
        return ans

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None
    except TimeoutError as error:
        print(f'Timeout occurred: {error}')
        return get_messages(creds, query)  # Retry on timeout
    
def get_thread(creds, threadID):
    if not creds or not creds.valid:
        print("Invalid credentials")
        return []
    try:
        service = build('gmail', 'v1', credentials=creds)
        collection = service.users().threads().get(userId= 'me', id=threadID)
        response = collection.execute()
        if 'messages' not in response:
            print("No messages found.")
            return []
        ans = []
        for message in response['messages']:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            id = msg['id']
            thread_id = msg['threadId']
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            body = msg.get('snippet', '(No Body)')
            ans.append({
                'id': id,
                'threadId': thread_id,
                'subject': subject,
                'body': body
            })
        return ans
    except HttpError as error:
        print(f"An error occured: {error}")
    except TimeoutError as error:
        print(f'Timeout occured : {error}')
        return get_thread(creds, threadID)