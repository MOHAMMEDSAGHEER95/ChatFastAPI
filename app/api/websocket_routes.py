from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import timedelta

from pymongo import MongoClient

from app.core.chat_manager import ChatManager
from app.core.config import mongo_url
from app.core.websocket import ConnectionManager
from app.openai.client import OpenAIClientHelper
from auth.jwt_handler import create_access_token, verify_password, hash_password, get_current_user

router = APIRouter()
manager = ConnectionManager()


chat_manager = ChatManager()


class MessageBody(BaseModel):
    message: str


@router.websocket("/ws/chat/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    await manager.connect(websocket, thread_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"{data}", thread_id, True)
            openai_client = OpenAIClientHelper()
            openai_client.add_message(thread_id, data)
            openai_client.run_thread(thread_id, 'asst_O2ZHsm0wPXbt21XCF5CExMsk')
            messages = openai_client.get_messages(thread_id)
            response = messages[0]
            generated_text = ''
            for content in response.content:
                try:
                    generated_text += content.text.value
                except Exception as e:
                    pass
            await manager.broadcast(f"{generated_text}", thread_id, False)
    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id)
        await manager.broadcast(f"A client disconnected from {thread_id}", thread_id, True)


@router.post("/threads/{thread_id}/messages/")
async def send_message_to_thread(thread_id: str, body: MessageBody, user: str = Depends(get_current_user)):
    """Endpoint to send a message to an existing thread"""
    try:
        # Add the message to the thread
        # Broadcast the message via WebSocket
        openai_client = OpenAIClientHelper()
        await manager.broadcast(f"{body.message}", thread_id, False)
        openai_client.add_message(thread_id, body.message)
        openai_client.run_thread(thread_id, 'asst_O2ZHsm0wPXbt21XCF5CExMsk')
        messages = openai_client.get_messages(thread_id)
        response = messages[0]
        generated_text = ''
        for content in response.content:
            try:
                generated_text += content.text.value
            except Exception as e:
                pass

        await manager.broadcast(f"{generated_text}", thread_id, False)
        return {"message": "Message sent successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/threads/")
def create_thread(user: str = Depends(get_current_user)):
    """Endpoint to initialize a new conversation (thread)"""
    thread_id = chat_manager.create_thread()
    return {"thread_id": thread_id}


@router.get("/threads/")
def create_thread(user: str = Depends(get_current_user)):
    """Endpoint to initialize a new conversation (thread)"""
    client = MongoClient(
        mongo_url
    )
    db = client["chat_db"]  # The database name is "chat_db"
    threads_collection = db["threads"]
    ids = threads_collection.find({}, {"_id": 1})
    return {"thread_id": [str(document["_id"]) for document in ids]}


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
