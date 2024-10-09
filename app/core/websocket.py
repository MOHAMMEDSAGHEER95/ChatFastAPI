from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections per thread
        self.active_connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, thread_id: str):
        await websocket.accept()
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = []
        self.active_connections[thread_id].append(websocket)

    def disconnect(self, websocket: WebSocket, thread_id: str):
        self.active_connections[thread_id].remove(websocket)

    async def broadcast(self, message: str, thread_id: str):
        if thread_id in self.active_connections:
            for connection in self.active_connections[thread_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")  # WebSocket endpoint
async def websocket_endpoint(websocket: WebSocket):
    # Connect the new client
    await manager.connect(websocket)
    try:
        while True:
            # Receive message from the client
            data = await websocket.receive_text()
            # Broadcast the received message to all connected clients
            await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        # Handle the client disconnect
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected!")
