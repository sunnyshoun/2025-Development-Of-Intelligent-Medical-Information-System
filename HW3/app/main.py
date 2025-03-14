from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import api, root

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(api.router, prefix="/api")
app.include_router(root.router)
