from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

app = FastAPI()

# This will hold all connected WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    # Add a new client to the list of active connections
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    # Remove a disconnected client from the list
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    # Broadcast a message to all connected clients
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Create an instance of ConnectionManager
manager = ConnectionManager()

# WebSocket endpoint
@app.websocket("/ws/chat")
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