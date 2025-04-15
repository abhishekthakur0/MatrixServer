from authlib.jose import jwt
import argparse
import time

def generate_token(secret, subject, issuer, algorithm="HS256"):
    # Create the header
    header = {"alg": algorithm}
    secret = "dev_jwt_secret_key_123"
    # Create the payload
    payload = {
        "sub": subject,  # Local part of the user ID
        "iss": issuer    # Required issuer claim
    }
    
    # Generate the token
    result = jwt.encode(header, payload, secret)
    return result.decode("ascii")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate JWT token for Matrix')
    parser.add_argument('--secret', required=True, help='JWT secret key')
    parser.add_argument('--subject', required=True, help='Local part of the user ID (e.g., "admin" for @admin:localhost)')
    parser.add_argument('--issuer', required=True, help='JWT issuer (must match homeserver.yaml)')
    parser.add_argument('--algorithm', default='HS256', help='JWT algorithm (default: HS256)')
    parser.add_argument('--delay', type=int, default=5, help='Delay in seconds between requests (default: 5)')
    
    args = parser.parse_args()
    
    # Add delay to prevent rate limiting
    print(f"Waiting {args.delay} seconds to prevent rate limiting...")
    time.sleep(args.delay)
    
    token = generate_token(
        args.secret,
        args.subject,
        args.issuer,
        args.algorithm
    )
    
    print(f"Generated JWT token: {token}") 