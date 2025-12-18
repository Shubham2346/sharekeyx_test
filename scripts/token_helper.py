import requests
import os
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("UPSTOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("UPSTOX_CLIENT_SECRET")
REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")

def get_login_url():
    return (
        "https://api.upstox.com/v2/login/authorization/dialog"
        f"?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
    )

def generate_access_token(auth_code):
    url = "https://api.upstox.com/v2/login/authorization/token"
    payload = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    r = requests.post(url, data=payload)
    r.raise_for_status()
    return r.json()

if __name__ == "__main__":
    print("Open this URL and login:")
    print(get_login_url())
    print("\nAfter login, paste ?code=XXXX here")
