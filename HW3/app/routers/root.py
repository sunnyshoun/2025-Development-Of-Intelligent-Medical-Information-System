from fastapi import APIRouter
from fastapi.responses import FileResponse
import os

router = APIRouter()

@router.get("/")
async def serve_index():
    index_path = os.path.join("app/static", "pages/index.html")
    return FileResponse(index_path)