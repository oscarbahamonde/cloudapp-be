from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from api.config import env
from requests import post, get
from api.controller import cognito

a = APIRouter()


@a.get("/token")
def get_token(code:str)->RedirectResponse:
    url = env.get('token_url')
    data = {
        'client_id': env.get('aws_app_client_id'),
        'client_secret': env.get('aws_app_client_secret'),
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': env.get('cognito_redirect_uri'),
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    res = post(url, data=data, headers=headers)
    token = res.json()['access_token']
    return RedirectResponse(f"http://localhost:3333/?token={token}")


@a.post("/token")
def get_current_user(token:str)->JSONResponse:
    return JSONResponse(cognito.get_user(AccessToken=token))


