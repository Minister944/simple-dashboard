import json
import os
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx2

STATIC_DIR = Path(__file__).parent / "static"
CORS_ORIGINS = [
    o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()
]
SERVICES = json.loads(os.environ.get("SERVICES", "{}"))

dockhand_client = httpx2.AsyncClient(
    base_url=os.environ["DOCKHAND_URL"],
    headers={"Authorization": f"Bearer {os.environ['DOCKHAND_TOKEN']}"},
)


async def get_stacks():
    response = await dockhand_client.get(
        url="/api/stacks",
        params={"env": "1"},
    )
    stacks = []

    for stack in response.json():
        if stack["name"] in SERVICES:
            stacks.append(
                {"name": stack["name"], "status": stack["status"], **SERVICES[stack["name"]]}
            )

    return stacks


app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_methods=["*"],
    )


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/stacks")
async def stacks():
    return await get_stacks()


@app.get("/start/{name}")
async def start(name: str):
    if not SERVICES.get(name, {}).get("startable"):
        raise HTTPException(status_code=404)
    await dockhand_client.post(
        url=f"/api/stacks/{name}/start",
        params={"env": "1"},
    )
    return {"status": "ok"}
