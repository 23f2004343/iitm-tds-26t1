import os
import json
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.config import Config

# Helper to get env vars or default for testing
# User must set these or replace them in the code
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "REPLACE_WITH_YOUR_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "REPLACE_WITH_YOUR_CLIENT_SECRET")
SECRET_KEY = "random_secret_string" 

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

@app.get("/")
def home(request: Request):
    user = request.session.get("user")
    if user:
        return HTMLResponse(f"""
        <h1>Welcome {user.get('email')}</h1>
        <p>Your ID Token is stored.</p>
        <a href="/id_token">View ID Token</a> <br>
        <a href="/logout">Logout</a>
        """)
    return HTMLResponse('<a href="/login">Login with Google</a>')

@app.get("/login")
def login(request: Request):
    redirect_uri = str(request.url_for("auth"))
    # Allow http for local testing
    if redirect_uri.startswith("http://") and "localhost" not in redirect_uri and "127.0.0.1" not in redirect_uri:
         redirect_uri = redirect_uri.replace("http://", "https://")
         
    return RedirectResponse(
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"response_type=code&client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile"
    )

@app.get("/auth")
async def auth(request: Request):
    code = request.query_params.get("code")
    if not code:
        return "Error: No code received"

    redirect_uri = str(request.url_for("auth"))
    # Ensure redirect_uri matches exactly what was sent in login
    if redirect_uri.startswith("http://") and "localhost" not in redirect_uri and "127.0.0.1" not in redirect_uri:
         redirect_uri = redirect_uri.replace("http://", "https://")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)
        tokens = response.json()
        
    if "id_token" not in tokens:
        return JSONResponse(tokens, status_code=400)

    # Decode basic info (skip signature verification for simplicity in this demo, 
    # but in prod verify it! Here we just need values)
    # We'll just trust Google's direct response over HTTPS.
    
    # Get user info
    async with httpx.AsyncClient() as client:
        user_info = await client.get("https://www.googleapis.com/oauth2/v1/userinfo", 
                                     headers={"Authorization": f"Bearer {tokens['access_token']}"})
        user_data = user_info.json()
    
    request.session["user"] = user_data
    request.session["id_token"] = tokens["id_token"]
    
    return RedirectResponse("/")

@app.get("/id_token")
def get_id_token(request: Request):
    token = request.session.get("id_token")
    if not token:
        return JSONResponse({"error": "Not logged in"}, status_code=401)
    
    # Return as raw JSON string if requested, or just the JSON object
    # The question asks for the raw id_token string in the final JSON submission, 
    # but the endpoint /id_token usually returns it.
    # Let's return a simple JSON wrapper.
    return {
        "id_token": token,
        "client_id": GOOGLE_CLIENT_ID
    }

@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
