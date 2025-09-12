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

def get_all_users():
    """
    Query Microsoft Graph API for all users and return a list of dictionaries for each user.
    """
    # Acquire access token
    token = get_access_token()

    # API endpoint
    url = "https://graph.microsoft.com/v1.0/users"

    params = {
    "$select": "id,displayName,userPrincipalName,department,accountEnabled"
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # List of users(dictionaries)
    all_users = []

    # Handle pagination if any
    while url:

        try:
            response = requests.get(
                url,
                headers=headers, 
                params=params if not all_users else None
            )
            
            response.raise_for_status()
        except RequestException as e:
            raise e

        data = response.json()
        users = data.get("value", [])
        all_users.extend(users)

        # Get the URL for the next page, or None if there isn’t one
        url = data.get("@odata.nextLink")

    return all_users

