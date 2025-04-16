import jwt
import json

def decode_token(token):
    try:
        # Decode the token without verifying the signature
        decoded = jwt.decode(token, options={"verify_signature": False})
        print("\nToken contents:")
        print(json.dumps(decoded, indent=2))
        
        # Print important fields
        print("\nImportant fields:")
        print(f"Issuer (iss): {decoded.get('iss')}")
        print(f"Audience (aud): {decoded.get('aud')}")
        print(f"User ID (user_id): {decoded.get('user_id')}")
        print(f"Subject (sub): {decoded.get('sub')}")
        print(f"Issued At (iat): {decoded.get('iat')}")
        print(f"Expiration (exp): {decoded.get('exp')}")
        
    except Exception as e:
        print(f"Error decoding token: {e}")

if __name__ == '__main__':
    # Your Firebase token
    token = "eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg1NzA4MWNhOWNiYjM3YzIzNDk4ZGQzOTQzYmYzNzFhMDU4ODNkMjgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vZGV2LWJ3LWZpcmViYXNlLWh1YiIsImF1ZCI6ImRldi1idy1maXJlYmFzZS1odWIiLCJhdXRoX3RpbWUiOjE3NDQ3ODQ1NTEsInVzZXJfaWQiOiIxNjg1MjE3MiIsInN1YiI6IjE2ODUyMTcyIiwiaWF0IjoxNzQ0Nzg0NTUxLCJleHAiOjE3NDQ3ODgxNTEsInBob25lX251bWJlciI6Iis5MTk2OTg5Njk4OTIiLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7InBob25lIjpbIis5MTk2OTg5Njk4OTIiXX0sInNpZ25faW5fcHJvdmlkZXIiOiJjdXN0b20ifX0.OrIVtFfVYYiPToStxyrg0fQtQgZRMEZ8_tiSiu5Ikw8oQf7ikQ1Pny6l61JYYozVIPf4E8fcG2d5w9QQp-OeTByY9pfub7FEujNEmYIIXmgBBnjxKt9p6M2nicD_HHJljJ2cuX-JARxBM2ufdsCSOA0bslHwusR64-e9BCdPNNmvnhF7timeTUypNxM4EnIHMBgg9CXqnjTv9JCqVxOQy16chL_UmTqpDFCaWPrtyv6V7DUqa_Jz_cuAQrmIqMC41D7j8iPfigWBFTS_bVjoIvIp9SYeyYDiKXWqf8Ge1Co0xZV918Dz5QRkga6DxAE_cIi8nIogk_WiMmB4Hn4NPqQ"
    decode_token(token) 