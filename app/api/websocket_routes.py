from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from app.core.chat_manager import ChatManager
from app.core.websocket import ConnectionManager

router = APIRouter()
manager = ConnectionManager()


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected!")


chat_manager = ChatManager()


class MessageBody(BaseModel):
    message: str


@router.websocket("/ws/chat/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    await manager.connect(websocket, thread_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Client in {thread_id} says: {data}", thread_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id)
        await manager.broadcast(f"A client disconnected from {thread_id}", thread_id)


@router.post("/threads/{thread_id}/messages/")
async def send_message_to_thread(thread_id: str, body: MessageBody):
    """Endpoint to send a message to an existing thread"""
    try:
        # Add the message to the thread
        chat_manager.add_message_to_thread(thread_id, body.message)
        # Broadcast the message via WebSocket
        await manager.broadcast(f"Thread {thread_id}: {body.message}", thread_id)
        return {"message": "Message sent successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/threads/")
def create_thread():
    """Endpoint to initialize a new conversation (thread)"""
    thread_id = chat_manager.create_thread()
    return {"thread_id": thread_id}


@router.get("/threads/{thread_id}/messages/")
def get_messages(thread_id: str):
    """Endpoint to retrieve all messages from a thread"""
    try:
        messages = chat_manager.get_messages(thread_id)
        return {"thread_id": thread_id, "messages": messages}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
