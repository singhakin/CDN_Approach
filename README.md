It uses standard Python libraries (hmac, hashlib, base64) so you don't need heavy dependencies. I have wrapped it in a service class pattern, which is how you should structure it in a real application (Django/FastAPI/Flask).

1. The CloudCDNService (Python Code)
Save this as services/cdn_signer.py


3. Critical Configuration Checklist
Padding: The code above specifically handles rstrip('='). Cloud CDN is very strict about URL-Safe Base64 with NO padding. If you send padding characters (=), it will reject the signature.

Domain Scope: In response.set_cookie, ensure the domain allows the cookie to be sent to the CDN subdomain.

If your app is app.site.com and images are images.site.com.

Set cookie domain to .site.com (note the leading dot).

Key Generation:

You must generate the key strictly using: head -c 16 /dev/urandom | base64 | tr +/ -_

If you use a random string generator online, ensure it is exactly 16 bytes decoded.





-----------------------------------------------Akamai------------------------------------------------

To replace the Google Cloud CDN architecture with Akamai while solving your "200 photos" and "Mandatory Headers" problems, you will move to a Token Authentication architecture.Here is the exact Battle-Tested Akamai + GCS Architecture.The Architecture ChangeFront Door (User $\to$ Akamai): You will use Akamai EdgeAuth (Auth Token 2.0).1 This replaces the "Signed Cookie."Back Door (Akamai $\to$ GCS): You will use GCS Interoperability (HMAC Keys).2 This allows Akamai to fetch private images from your Google Bucket without making the bucket public.Step 1: Configure GCS (The Origin)You must give Akamai a "username and password" to read your private bucket. In GCS, this is called an HMAC Key.3Go to Google Cloud Console 4$\to$ Cloud Storage 5$\to$ Settings.6Click the Interoperability tab.Click Create a key for a service account.Select the Service Account that has access to your images.Copy the Access Key and Secret. You will need these for Akamai.Step 2: Configure Akamai (Property Manager)You need to make two major changes in your Akamai Property Configuration.A. Configure the Connection to GCSThis ensures Akamai can fetch the images.Origin Server Hostname: Set to storage.googleapis.com.Origin Characteristics Behavior:Authentication Method: Select Interoperability Google Cloud Platform.Access ID: Paste the GCS Access Key (from Step 1).7Secret: Paste the GCS Secret (from Step 1).8Encrypted Storage: Yes (Stores keys securely in Akamai Cloud Access Manager).9B. Configure the Security (Token Auth)This ensures only logged-in users can see the images.Add a new Rule (e.g., "Protected Images").Match criteria: Path matches /users/* (or your specific path).Add Behavior: Auth Token 2.0 Verification.Token Location: Cookie.Token Name: akamai_token (or any name you prefer).Encryption Key: Generate a random hex string (e.g., a1b2c3d4...). Save this. You need it for your Python backend.Step 3: Backend Code (Python)Instead of generating a GCS cookie, you now generate an Akamai EdgeAuth Token.Library:


pip install akamai-edgeauth

