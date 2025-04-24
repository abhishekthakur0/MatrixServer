import requests
import json
import jwt
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504]
    )
    session.mount('http://', HTTPAdapter(max_retries=retries))
    return session

def test_firebase_login():
    print("\n1. Attempting Matrix login with Firebase token...")
    
    # Your Firebase ID token
    firebase_id_token = "<FIREBASE_ID_TOKEN>"
    
    # Decode the token to get the user ID (without verification)
    decoded_token = jwt.decode(firebase_id_token, options={"verify_signature": False})
    firebase_uid = decoded_token['user_id']
    matrix_username = f"@firebase_{firebase_uid}:localhost"
    
    # Prepare the login request payload
    login_payload = {
        "type": "m.login.firebase",
        "token": firebase_id_token,
        "identifier": {
            "type": "m.id.user",
            "user": matrix_username
        }
    }
    
    print("\nSending login request with payload:")
    print(json.dumps(login_payload, indent=2))
    
    # Send the login request to the Matrix server
    response = requests.post(
        "http://localhost:8008/_matrix/client/v3/login",
        json=login_payload
    )
    
    print(f"\nMatrix server response status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    else:
        print("❌ Login failed!")
        print("Error response:")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_firebase_login() 