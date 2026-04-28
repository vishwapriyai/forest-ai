from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router
from backend.core.config import DATA_DIR, FRONTEND_DIR
from backend.services.platform_state import platform_state, refresh_loop


app = FastAPI(title="Forest AI Platform", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")
app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")
app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR)), name="assets")


@app.on_event("startup")
async def startup_event() -> None:
    asyncio.create_task(refresh_loop())


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard")


@app.get("/dashboard")
def dashboard_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/live")
def live_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "live.html")


@app.get("/simulate-page")
def simulate_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "simulate.html")


@app.get("/index.html")
def legacy_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "live.html")


@app.websocket("/ws/live")
async def live_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(jsonable_encoder(platform_state.get_live_payload()))
            await asyncio.sleep(60)
    except WebSocketDisconnect:
        return
