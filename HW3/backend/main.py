from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from backend.search import search_meta

app = FastAPI()

@app.get("/api/search")
async def search(query: str = Query(..., min_length=1)):
    results = await search_meta(query)
    return {"results": results}

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/pages/index.html")