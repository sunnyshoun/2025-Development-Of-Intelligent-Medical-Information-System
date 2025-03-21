from fastapi import APIRouter, Response, Query
from app.backend.search import search_meta

router = APIRouter()

@router.get("/search", tags=["search"])
async def search(query: str = Query(..., min_length=1)):
    results = await search_meta(query)
    return {"results": results}

@router.head("/uptime", tags=["uptime"])
def uptime():
    return Response(status_code=200)