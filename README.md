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
