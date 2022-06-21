from api import main
from fastapi import WebSocket, Depends, Request
from typing import List, Dict
from api.schemas import User, Contact
from api.auth import get_current_user
from api.controller import sendEmail
from geocoder import ip
from starlette.responses import JSONResponse

app = main()

class SocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket,User] = []
    async def connect(self, websocket:WebSocket, user: User):
        await websocket.accept()
        self.active_connections.append((websocket,user))
    def diconnect(self,websocket:WebSocket, user: User):
        self.active_connections.remove((websocket,user))
    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection[0].send_json(data)

manager = SocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket:WebSocket, val = Depends(get_current_user)):
    await manager.connect(websocket, val)
    response = {
        "sender": val.displayName,
        "message": "Welcome to the chat!"
    }
    await manager.broadcast(response)
    try:
        while True:
            data = await websocket.receive_json()
            response = {
                "sender": val.displayName,
                "message": data["message"]
            }
            await manager.broadcast(response)
    except Exception as e:
        print(e)
    finally:
        manager.diconnect(websocket, val)
        await websocket.close()
        
@app.post("/")
async def contactForm(contact:Contact):
    return sendEmail(contact.name, contact.email, contact.message)

from api.db import create_document
from pydantic import BaseModel

class Log(BaseModel):
    ip: List[Dict]


async def get_user_agent_data(req: Request):
    ip_from = str(req.headers['x-forwarded-for'])
    ip_to = str(req.headers['cf-connecting-ip'])
    if ip_from != ip_to:
        print(f"IP from: {ip_from}", f"IP to: {ip_to}")
    res =  [
        {
        'url': str(req.url),
            },
        ip(ip_from).json,
        ip(ip_to).json
    ]
    agent = Log(ip=res)
    create_document(agent)
    return agent    

from api.auth import get_current_user
from typing import Callable
from fastapi import HTTPException

@app.middleware("http")
async def auth_middleware(request: Request, call_next: Callable):
    path = request.url.path
    if path.startswith("/api") is False:
        return await call_next(request)
    token = request.headers.get('Authorization')
    if token is None:
        raise HTTPException(status_code=401, detail="Not authorized")
    try:
        user = await get_current_user(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Not authorized")
    request.state.user = user
    return await call_next(request)
