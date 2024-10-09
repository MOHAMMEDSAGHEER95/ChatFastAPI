# app/api/chat_routes.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel

from app.core.chat_manager import ChatManager
from app.core.websocket import ConnectionManager

router = APIRouter()

# Create an instance of ChatManager to manage threads and messages
# chat_manager = ChatManager()













