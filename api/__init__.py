from fastapi import FastAPI
from api.auth import a
from api.router import r

def main():
    app = FastAPI()
    app.include_router(a, tags=['auth'])
    app.include_router(r, prefix='/api', tags=['media'])
    
    return app