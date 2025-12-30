from services.akamai_signer import AkamaiTokenService
# Assuming you have the class we created in the previous step

class AccessPolicyService:
    def __init__(self):
        # Initialize with your Akamai Hex Key
        self.signer = AkamaiTokenService(AKAMAI_KEY, COOKIE_NAME)

    def grant_access(self, user_type: str, resource_id: str):
        """
        Unified logic to grant access based on user persona.
        resource_id: The folder name (e.g., guest_session_id or user_id)
        """
        
        # 1. Define the Path (Storage Location)
        # Recommended: Keep guests in a separate prefix like /temp/ or /guests/
        # to separate them from permanent /users/
        if user_type in ["GUEST_NEW", "GUEST_OTP"]:
            path = f"/guests/{resource_id}/*"
        else:
            path = f"/users/{resource_id}/*"

        # 2. Define the Time-To-Live (TTL) based on Business Rules
        if user_type == "GUEST_NEW":
            # Scenario: Just uploaded. Access for 20 mins.
            duration = 20 * 60 
            
        elif user_type == "GUEST_OTP":
            # Scenario: Came back 3 days later, entered OTP.
            # Give them 1 hour to view/edit.
            duration = 60 * 60 
            
        elif user_type == "LOGGED_IN":
            # Scenario: Standard User. Keep valid for session.
            duration = 2 * 60 * 60 # 2 Hours

        # 3. Generate the Token
        # We access the internal generator but override the window
        token = self.signer.et.generate_acl_token(
            path, 
            window_seconds=duration
        )
        
        return token, duration
