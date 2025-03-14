from fastapi import APIRouter, Query
from app.backend.search import search_meta

router = APIRouter(tags=["search"])  # 刪除 prefix="/api"

@router.get("/search")
async def search(query: str = Query(..., min_length=1)):
    results = await search_meta(query)
    return {"results": results}
