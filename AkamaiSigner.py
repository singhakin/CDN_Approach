from akamai.edgeauth import EdgeAuth, EdgeAuthError
import time

class AkamaiTokenService:
    def __init__(self, encryption_key: str, token_name: str = "akamai_token"):
        """
        Args:
            encryption_key: The Hex string you set in Akamai Property Manager.
            token_name: The cookie name you set in Akamai Property Manager.
        """
        self.et = EdgeAuth(
            key=encryption_key,
            token_name=token_name,
            window_seconds=3600, # 1 Hour Validity
            escape_early=False   # Usually False for Cookies
        )

    def generate_cookie_value(self, folder_path: str) -> str:
        """
        Generates the ACL token for a specific folder.
        
        Args:
            folder_path: The path pattern, e.g., "/users/123/*"
        """
        try:
            # Generate token for a wildcard path (ACL)
            # This allows access to ALL photos in that folder
            token = self.et.generate_acl_token(folder_path)
            return token
        except EdgeAuthError as e:
            print(f"Error generating token: {e}")
            return None

# --- Usage in your API ---
if __name__ == "__main__":
    # CONFIG FROM AKAMAI PROPERTY MANAGER
    AKAMAI_KEY = "deadbeef12345678deadbeef12345678" 
    COOKIE_NAME = "akamai_token"
    
    signer = AkamaiTokenService(AKAMAI_KEY, COOKIE_NAME)
    
    # User 123 wants to see their gallery
    # Note: Path must match what Akamai sees (usually starts after domain)
    user_folder = "/users/123/*"
    
    token_value = signer.generate_cookie_value(user_folder)
    
    print(f"Set-Cookie: {COOKIE_NAME}={token_value}; Domain=.yoursite.com; Path=/; HttpOnly; Secure")
