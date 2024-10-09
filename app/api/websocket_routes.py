from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import timedelta

from app.core.chat_manager import ChatManager
from app.core.websocket import ConnectionManager
from auth.jwt_handler import create_access_token, verify_password, hash_password, get_current_user

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
            await manager.broadcast(f"{data}", thread_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id)
        await manager.broadcast(f"A client disconnected from {thread_id}", thread_id)


@router.post("/threads/{thread_id}/messages/")
async def send_message_to_thread(thread_id: str, body: MessageBody, user: str = Depends(get_current_user)):
    """Endpoint to send a message to an existing thread"""
    try:
        # Add the message to the thread
        # Broadcast the message via WebSocket
        await manager.broadcast(f"{body.message}", thread_id)
        return {"message": "Message sent successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/threads/")
def create_thread(user: str = Depends(get_current_user)):
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

# In-memory database (for demonstration purposes)


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$gG44bENjfU4.2dPS1fAHEus8y5eGiX/xskHUKQxMO4X9CffNOZsdq",  # password is 'secret'
    }
}


# Pydantic model to handle login request data
class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/token")
async def login_for_access_token(form_data: LoginRequest):
    """Route to log in and get a JWT token."""
    user = fake_users_db.get(form_data.username)
    if not user or not verify_password(form_data.password, user['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=timedelta(minutes=30)
    )
    return {"access_token": access_token, "token_type": "bearer"}
