"""A Basic API endpoint to connect with `ChatAgent`"""
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .connection_manager import ConnectionManager
from .chat_agent import ChatAgent, get_vec_db


DB_DIR = os.environ.get("DB_DIR", "chroma_data/")

# The application
app = FastAPI()


# Connection Manager
connection_manager = ConnectionManager()

# The LLM Part
vec_db = get_vec_db(DB_DIR)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


FRONTEND_DIR = os.environ.get("FRONTEND_DIR", "./dist/frontend/browser/")


@app.get('/')
def index() -> FileResponse:
    """Serve the frontend of the application"""
    return FileResponse(f"{FRONTEND_DIR}/index.html")


@app.websocket('/chat/{client_id}')
async def connect(ws: WebSocket, client_id: int):
    """Connects client `client_id` with the llm"""
    await connection_manager.connect(ws)
    try:
        agent = ChatAgent(vec_db)
        while True:
            data = await ws.receive_text()
            res = await agent.talk(data)
            await connection_manager.send_pm(res, ws)
            await connection_manager.send_pm("[END]", ws)
    except WebSocketDisconnect:
        connection_manager.disconnect(ws)

app.mount("/", StaticFiles(directory=FRONTEND_DIR))
