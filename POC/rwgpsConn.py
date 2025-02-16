import requests
import json
from typing import Optional, Dict, Union
import os
from dotenv import load_dotenv

def get_auth_token(email: str, password: str, api_key: str) -> Optional[Dict[str, Union[str, Dict]]]:
    """
    Get an authentication token from RideWithGPS API using email and password.
    
    Args:
        email (str): User's email address
        password (str): User's password
        api_key (str): RideWithGPS API key
    
    Returns:
        Optional[Dict]: Dictionary containing auth token and user information if successful,
                       None if the request fails
    """
    url = "https://ridewithgps.com/api/v1/auth_tokens.json"
    
    # Set up headers with API key
    headers = {
        "x-rwgps-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # Prepare request payload
    payload = {
        "user": {
            "email": email,
            "password": password
        }
    }
    
    try:
        # Make the POST request
        response = requests.post(url, headers=headers, json=payload)
        
        # Check if request was successful (status code 201)
        if response.status_code == 201:
            return response.json()["auth_token"]
        else:
            print(f"Authentication failed. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication request: {str(e)}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing response: {str(e)}")
        return None

if __name__ == "__main__":

    load_dotenv()

    # Example usage
    API_KEY = os.getenv("RWGPS_APIK")
    EMAIL = os.getenv("RWGPS_USER")
    PASSWORD = os.getenv("RWGPS_PASS")
    
    auth_token = get_auth_token(EMAIL, PASSWORD, API_KEY)
    
    if auth_token:
        print(f"Authentication successful!")
        print(f"Auth Token: {auth_token['auth_token']}")
        print(f"User: {auth_token['user']['name']} ({auth_token['user']['email']})")