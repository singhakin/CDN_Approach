import hmac
import hashlib
import base64
import time
import struct
from typing import Optional

class CloudCDNService:
    def __init__(self, key_name: str, base64_key_secret: str):
        """
        Initialize with your CDN Key details.
        
        Args:
            key_name (str): The name of the key created in GCP (e.g., "my-cdn-key").
            base64_key_secret (str): The 16-byte base64 encoded secret.
        """
        self.key_name = key_name
        self.key_secret = base64.urlsafe_b64decode(base64_key_secret)

    def generate_signed_cookie(self, url_prefix: str, expiration_seconds: int = 3600) -> str:
        """
        Generates a Signed Cookie value for Google Cloud CDN.
        
        Args:
            url_prefix (str): The URL prefix to authorize (e.g., "https://cdn.site.com/users/123/").
            expiration_seconds (int): How long the cookie is valid (default 1 hour).
            
        Returns:
            str: The full cookie value string (e.g., "URLPrefix=...:Signature=...")
        """
        # 1. Calculate Expiration Timestamp
        expiration_time = int(time.time()) + expiration_seconds

        # 2. Base64 Encode the URL Prefix (URL-safe, no padding)
        encoded_url_prefix = base64.urlsafe_b64encode(url_prefix.encode('utf-8')).decode('utf-8').rstrip('=')

        # 3. Construct the Policy String
        # Order matters: URLPrefix -> Expires -> KeyName
        policy = f"URLPrefix={encoded_url_prefix}:Expires={expiration_time}:KeyName={self.key_name}"

        # 4. create the Signature
        # Google Cloud CDN uses HMAC-SHA1
        signature_bytes = hmac.new(
            self.key_secret,
            policy.encode('utf-8'),
            hashlib.sha1
        ).digest()

        # 5. Base64 Encode the Signature (URL-safe, no padding)
        encoded_signature = base64.urlsafe_b64encode(signature_bytes).decode('utf-8').rstrip('=')

        # 6. Return the final Cookie Value
        return f"Cloud-CDN-Cookie={policy}:Signature={encoded_signature}"

# --- usage Example (e.g., in a Flask/FastAPI route) ---
if __name__ == "__main__":
    # 1. Setup (Load these from Env Variables in production!)
    # Run this in terminal to generate a key: head -c 16 /dev/urandom | base64 | tr +/ -_
    MY_KEY_NAME = "production-cdn-key"
    MY_KEY_SECRET = "nZtRo_ExampleKey_123==" 
    
    signer = CloudCDNService(MY_KEY_NAME, MY_KEY_SECRET)

    # 2. Define the User's Folder (The "Prefix")
    user_id = "user_99"
    cdn_domain = "https://images.myprintsite.com"
    folder_prefix = f"{cdn_domain}/users/{user_id}/"

    # 3. Generate Cookie
    cookie_value = signer.generate_signed_cookie(folder_prefix)

    print(f"--- Production Cookie for User {user_id} ---")
    print(f"Set-Cookie: {cookie_value}; Domain=.myprintsite.com; Path=/; Secure; HttpOnly")
    
    # 4. Simulate the Scene File Response
    # Note: We send the cookie in headers, but the JSON only contains simple paths.
    response_body = {
        "scene_id": "card_A1",
        "images": [
            f"{folder_prefix}vacation.jpg",
            f"{folder_prefix}wedding.jpg"
        ]
    }
    print("\n--- JSON Body (Clean Paths!) ---")
    print(response_body)
