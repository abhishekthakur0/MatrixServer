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
    firebase_id_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg1NzA4MWNhOWNiYjM3YzIzNDk4ZGQzOTQzYmYzNzFhMDU4ODNkMjgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vZGV2LWJ3LWZpcmViYXNlLWh1YiIsImF1ZCI6ImRldi1idy1maXJlYmFzZS1odWIiLCJhdXRoX3RpbWUiOjE3NDQ3ODQ1NTEsInVzZXJfaWQiOiIxNjg1MjE3MiIsInN1YiI6IjE2ODUyMTcyIiwiaWF0IjoxNzQ0Nzg0NTUxLCJleHAiOjE3NDQ3ODgxNTEsInBob25lX251bWJlciI6Iis5MTk2OTg5Njk4OTIiLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7InBob25lIjpbIis5MTk2OTg5Njk4OTIiXX0sInNpZ25faW5fcHJvdmlkZXIiOiJjdXN0b20ifX0.OrIVtFfVYYiPToStxyrg0fQtQgZRMEZ8_tiSiu5Ikw8oQf7ikQ1Pny6l61JYYozVIPf4E8fcG2d5w9QQp-OeTByY9pfub7FEujNEmYIIXmgBBnjxKt9p6M2nicD_HHJljJ2cuX-JARxBM2ufdsCSOA0bslHwusR64-e9BCdPNNmvnhF7timeTUypNxM4EnIHMBgg9CXqnjTv9JCqVxOQy16chL_UmTqpDFCaWPrtyv6V7DUqa_Jz_cuAQrmIqMC41D7j8iPfigWBFTS_bVjoIvIp9SYeyYDiKXWqf8Ge1Co0xZV918Dz5QRkga6DxAE_cIi8nIogk_WiMmB4Hn4NPqQ"
    
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