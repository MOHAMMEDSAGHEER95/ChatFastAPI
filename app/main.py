from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.websocket_routes import router as websocket_router

app = FastAPI()

origins = [
    "http://localhost:3000",  # Frontend URL during development
    # Add production frontend URLs here as well, e.g., "https://myfrontend.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Origins that are allowed to make requests
    allow_credentials=True,  # Allows cookies to be sent in cross-origin requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers (like Authorization, Content-Type, etc.)
)

# Include the WebSocket routes
app.include_router(websocket_router)
