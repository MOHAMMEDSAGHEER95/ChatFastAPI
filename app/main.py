from fastapi import FastAPI
from app.api.websocket_routes import router as websocket_router
from app.api.chat_routes import router as chat_router

app = FastAPI()

# Include the WebSocket routes
app.include_router(websocket_router)
app.include_router(chat_router)
