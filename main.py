import os
import time
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth

# Load environment
load_dotenv()

app = FastAPI()
session_secret = os.getenv("SESSION_SECRET")
if not session_secret:
    raise RuntimeError("SESSION_SECRET environment variable is required but not set.")
app.add_middleware(SessionMiddleware, secret_key=session_secret)

# OAuth2 credentials
CLIENT_ID     = os.getenv("YAHOO_CLIENT_ID")
CLIENT_SECRET = os.getenv("YAHOO_CLIENT_SECRET")
REDIRECT_URI  = os.getenv("YAHOO_REDIRECT_URI")
YAHOO_AUTH_URL  = "https://api.login.yahoo.com/oauth2/request_auth"
YAHOO_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
YAHOO_API_BASE  = "https://fantasysports.yahooapis.com/fantasy/v2"

# Configure Authlib OAuth client
oauth = OAuth()
oauth.register(
    name='yahoo',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    authorize_url=YAHOO_AUTH_URL,
    access_token_url=YAHOO_TOKEN_URL,
    client_kwargs={'scope': 'fspt-w'}
)

@app.get("/oauth/login")
async def oauth_login(request: Request):
    redirect_uri = REDIRECT_URI
    return await oauth.yahoo.authorize_redirect(request, redirect_uri)

@app.get("/oauth/callback")
async def oauth_callback(request: Request):
    token = await oauth.yahoo.authorize_access_token(request)
    if not token:
        raise HTTPException(status_code=400, detail="Token exchange failed")
    # Store token in session
    request.session['token'] = token
    return JSONResponse(token)

async def get_client(request: Request):
    token = request.session.get('token')
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    client = oauth.yahoo
    client.token = token
    # Refresh if near expiry
    expires = token.get('expires_at', 0)
    if time.time() > expires - 60:
        token = await client.refresh_token(YAHOO_TOKEN_URL, refresh_token=token['refresh_token'])
        request.session['token'] = token
        client.token = token
    return client

@app.get("/leagueinfo")
async def get_league_info(request: Request, league_id: str):
    client = await get_client(request)
    resp = await client.get(f"{YAHOO_API_BASE}/league/{league_id}/settings?format=json")
    data = await resp.json()
    return JSONResponse(data)

@app.get("/draftresults")
async def get_draft_results(request: Request, league_id: str):
    client = await get_client(request)
    resp = await client.get(f"{YAHOO_API_BASE}/league/{league_id}/draftresults?format=json")
    data = await resp.json()
    return JSONResponse(data)

