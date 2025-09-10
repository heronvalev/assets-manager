"""
Test script to query Entra ID users via Microsoft Graph
"""

from azure.identity import ClientSecretCredential
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get the client ID and tenant ID from environment variables
CLIENT_ID = os.getenv("CLIENT_ID")
TENANT_ID = os.getenv("TENANT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Microsoft Graph scope needed to read users
SCOPES = ["https://graph.microsoft.com/.default"]

# Create a DeviceCodeCredential for interactive login
credential = ClientSecretCredential(
    client_id=CLIENT_ID,
    tenant_id=TENANT_ID,
    client_secret=CLIENT_SECRET
)

def get_access_token():
    """
    Authenticate using client credentials flow and return a bearer token.
    """

    token = credential.get_token(*SCOPES)
    return token.token

# print(get_access_token())

def get_user(upn: str):
    """
    Query Microsoft Graph for a user upn(email) and return their properties as a dictionary.
    """

    # Get an access token
    token = get_access_token()

    # Microsoft Graph endpoint for a single user
    url = f"https://graph.microsoft.com/v1.0/users/{upn}"

    # Authentication
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Make the get request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    
    else:
        print(f"Error: {response.status_code} - {response.text} ")
        return None
    
# Test

# upn = entra_user_email

# print(get_user(upn))



