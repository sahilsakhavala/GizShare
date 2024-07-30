# meet_integration/utils.py

from __future__ import print_function
import os.path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from google.apps import meet_v2
from GizShare.settings import GOOGLE_CREDENTIALS_FILE

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/meetings']


def create_meet_space():
    """Shows basic usage of the Google Meet API."""
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
                GOOGLE_CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Initialize the Meet v2 client
        client = meet_v2.SpacesServiceClient(credentials=creds)

        # Prepare the request to create a Meet space
        request = meet_v2.CreateSpaceRequest()
        response = client.create_space(request=request)

        # Return the meeting URI of the created space
        return response.name
    except Exception as error:
        # Handle errors gracefully
        print(f'An error occurred: {error}')
        return None
