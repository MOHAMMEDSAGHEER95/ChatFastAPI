from fastapi import FastAPI
from app.api.websocket_routes import router as websocket_router

app = FastAPI()

# Include the WebSocket routes
app.include_router(websocket_router)