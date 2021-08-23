import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import base64
from bs4 import BeautifulSoup
import os
from twilio.rest import Client
import time
from utils import sendSms


os.environ['TWILIO_ACCOUNT_SID'] = "Enter twilio account sid"
os.environ['TWILIO_AUTH_TOKEN'] = 'Enter twilio account token'

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def set_service():
    """
    Manages the authentication and return the service
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8000)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('gmail', 'v1', credentials=creds)


    return service


def getRecentMessage(service):
    # Get recent message
    messages_list_result = service.users().messages().list(userId="me", maxResults=1).execute()

    # Get id of recent message
    found_messageId = messages_list_result.get("messages")[0].get("id")

    # Get message
    message_result = service.users().messages().get(userId="me", id=found_messageId).execute()
    
    # Get parts of message
    main_message = message_result.get("payload").get("parts")

    
    main_message_decoded = ""

    # Iterate through each part of message
    for part in main_message:
        # encoded message data
        data = part['body']['data']
        data = data.replace("-","+").replace("_","/")

        # Decode the encoded message
        decoded_data = base64.b64decode(data).strip().decode()

        # Create a BeautifulSoup instance to get text from html
        soup = BeautifulSoup(decoded_data, features="html.parser")

        # Try to replace br tags with \n
        try:
            soup.br.replace_with("\n")
        except Exception as e:
            pass
        

        # Get text from html
        body = soup.get_text()


        main_message_decoded = body

    return main_message_decoded

if __name__ == '__main__':
    # Create a service
    service = set_service()

    # Get default messages state
    currentMessage = getRecentMessage(service)


    # Track message changes after a delay of 10 seconds.
    while True:
        # Get recent message again
        message = getRecentMessage(service)

        # If the message is not equals to default message then it's meen a new message is arrived!
        if message != currentMessage:
            print("Got new message")

            # Change the default message state
            currentMessage = message

            # Send the message
            sendSms(message, client)

            print("SMS Sent successfully!")

    

