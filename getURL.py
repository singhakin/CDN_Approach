from fastapi import FastAPI, Response
from pydantic import BaseModel
import os

app = FastAPI()

# Initialize Service once (Singleton)
cdn_signer = CloudCDNService(
    key_name=os.getenv("CDN_KEY_NAME"),
    base64_key_secret=os.getenv("CDN_KEY_SECRET")
)

@app.get("/api/scenes/{scene_id}")
def get_scene(scene_id: str, response: Response):
    # 1. Fetch scene data from DB
    # (Mock logic)
    user_id = "123" 
    scene_data = {
        "id": scene_id,
        "background": f"users/{user_id}/backgrounds/beach.jpg",
        "sticker": f"users/{user_id}/stickers/heart.png"
    }
    
    # 2. Generate the Signed Cookie for this user's entire folder
    # This grants access to ALL photos in "users/123/" for 6 hours
    prefix = f"https://cdn.site.com/users/{user_id}/"
    cookie_val = cdn_signer.generate_signed_cookie(prefix, expiration_seconds=21600)
    
    # 3. separate Key=Value from the full string
    # The helper returns "Cloud-CDN-Cookie=XYZ...", we just need the XYZ... part for FastAPI
    cookie_content = cookie_val.split("=", 1)[1]

    # 4. Set the Cookie on the Response
    response.set_cookie(
        key="Cloud-CDN-Cookie",
        value=cookie_content,
        domain=".site.com",   # critical: Must match your CDN domain or parent
        path="/",             # Critical: Scope to whole site
        secure=True,          # Critical: Only over HTTPS
        httponly=True,        # Good Practice: JS cannot steal it
        samesite="None"       # Often needed for cross-site resources
    )

    # 5. Return the clean JSON
    # Frontend just renders <img src="https://cdn.site.com/users/123/backgrounds/beach.jpg">
    return scene_data
