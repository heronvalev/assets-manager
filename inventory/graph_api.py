from azure.identity import ClientSecretCredential
import requests
from requests.exceptions import RequestException
import os
from dotenv import load_dotenv

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
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
    except RequestException as e:
        raise e

    data = response.json()
    if not data:
        raise ValueError(f"Empty response for user {upn}")

    return data
