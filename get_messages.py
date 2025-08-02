from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
from email.utils import parseaddr
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

def get_full_messages(creds, label_ids):
    print("Getting messages...")
    if not creds or not creds.valid:
        print("Invalid credentials")
        return []

    try:
        service = build('gmail', 'v1', credentials=creds)
        collection = service.users().messages().list(userId='me', labelIds=label_ids, maxResults=10)
        response = collection.execute()

        if 'messages' not in response:
            print("No messages found.")
            return []

        ans = []
        for message in response['messages']:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            msg_id = msg['id']
            thread_id = msg['threadId']
            headers = msg['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            
            # Extract full body content
            body = extract_body(msg['payload']) or "(No Body Found)"

            ans.append({
                'id': msg_id,
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
        return get_full_messages(creds, label_ids)  # Retry on timeout
    
def extract_body(payload):
    """
    Recursively extract the email body (plain text or html) from the payload.
    """
    if 'parts' in payload:
        for part in payload['parts']:
            result = extract_body(part)
            if result:
                return result
    else:
        mime_type = payload.get('mimeType')
        body_data = payload.get('body', {}).get('data')
        if body_data and (mime_type == 'text/plain' or mime_type == 'text/html'):
            return decode_base64url(body_data).decode('utf-8', errors='ignore')
    return None

def get_thread(creds, threadID):
    if not creds or not creds.valid:
        print("Invalid credentials")
        return []

    try:
        service = build('gmail', 'v1', credentials=creds)
        thread_response = service.users().threads().get(userId='me', id=threadID, format='full').execute()
        
        if 'messages' not in thread_response:
            print("No messages found.")
            return []
        
        ans = []
        for message in thread_response['messages']:
            msg_id = message['id']
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(No Subject)')
            from_header = next((h['value'] for h in headers if h['name'].lower() == 'from'), None)
            sender_name, sender_email = parseaddr(from_header)

            # Extract full body
            body = extract_body(message['payload']) or "(No Body Found)"

            ans.append({
                'id': msg_id,
                'SenderName': sender_name,
                'SenderMail': sender_email,
                'threadId': message['threadId'],
                'subject': subject,
                'body': body
            })

        return ans

    except HttpError as error:
        print(f"An error occurred: {error}")
    except TimeoutError as error:
        print(f"Timeout occurred: {error}")
        return get_thread(creds, threadID)