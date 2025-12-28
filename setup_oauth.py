"""
Blogger OAuth2 Setup - Get credentials for posting
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os

SCOPES = ['https://www.googleapis.com/auth/blogger']

def setup_oauth():
    """Setup OAuth2 credentials for Blogger"""
    
    creds = None
    
    # Check if we already have credentials
    if os.path.exists('blogger_token.pickle'):
        print("Found existing credentials...")
        with open('blogger_token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired credentials...")
            creds.refresh(Request())
        else:
            print("\n" + "="*60)
            print("BLOGGER OAUTH2 SETUP")
            print("="*60)
            print("\nThis will open your browser to authorize the app.")
            print("Please log in and grant permission.\n")
            
            # You need to create OAuth credentials first
            if not os.path.exists('client_secret.json'):
                print("ERROR: client_secret.json not found!")
                print("\nPlease follow these steps:")
                print("1. Go to: https://console.cloud.google.com/apis/credentials")
                print("2. Click 'Create Credentials' > 'OAuth client ID'")
                print("3. Application type: 'Desktop app'")
                print("4. Download the JSON file")
                print("5. Rename it to 'client_secret.json'")
                print("6. Put it in this folder")
                return False
            
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open('blogger_token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        
        print("\n" + "="*60)
        print("SUCCESS! OAuth2 credentials saved.")
        print("="*60)
        print("\nYou can now run: python auto_post_1min.py")
    
    return True

if __name__ == '__main__':
    setup_oauth()
