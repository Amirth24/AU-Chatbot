"""A Basic API endpoint to connect with `ChatAgent`"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .connection_manager import ConnectionManager
from .chat_agent import ChatAgent, get_vec_db


DB_DIR = "chroma_data/"

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


@app.get('/')
def health():
    """To check wheather api is reachable"""
    return {"status": "ok"}


@app.websocket('/chat/{client_id}')
async def connect(ws: WebSocket, client_id: int):
    """Connects client `client_id` with the llm"""
    await connection_manager.connect(ws)
    try:
        agent = ChatAgent(vec_db)
        while True:
            data = await ws.receive_text()
            async for tok in agent.talk(data):
                await connection_manager.send_pm(tok, ws)
            await connection_manager.send_pm("[END]", ws)
    except WebSocketDisconnect:
        connection_manager.disconnect(ws)
