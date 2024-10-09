from typing import List, Dict
from fastapi import WebSocket, WebSocketDisconnect
from pymongo import MongoClient
import os

class ConnectionManager:
    def __init__(self):
        # Dictionary to store active WebSocket connections per thread
        self.active_connections: Dict[str, List[WebSocket]] = {}

        # Connect to MongoDB (retrieve URI from environment variables)
        mongodb_uri = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@cluster0.w73f6.mongodb.net/?retryWrites=true&w=majority"

        self.client = MongoClient(mongodb_uri)
        self.db = self.client["chat_db"]  # The database name is "chat_db"
        self.threads_collection = self.db["threads"]  # The collection for threads

    async def connect(self, websocket: WebSocket, thread_id: str):
        """Accept WebSocket connection and store it under the given thread ID."""
        await websocket.accept()
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = []
        self.active_connections[thread_id].append(websocket)
        print(f"WebSocket connection added to thread {thread_id}. Total connections: {len(self.active_connections[thread_id])}")

    def disconnect(self, websocket: WebSocket, thread_id: str):
        """Remove the WebSocket connection from the list for the given thread."""
        if thread_id in self.active_connections:
            self.active_connections[thread_id].remove(websocket)
            if not self.active_connections[thread_id]:
                # Remove the thread if no active connections remain
                del self.active_connections[thread_id]
            print(f"WebSocket connection removed from thread {thread_id}. Total connections: {len(self.active_connections.get(thread_id, []))}")

    async def broadcast(self, message: str, thread_id: str):
        """Broadcast a message to all WebSocket connections under the given thread and save it to MongoDB."""
        if thread_id in self.active_connections:
            connections_to_remove = []
            for connection in self.active_connections[thread_id]:
                try:
                    await connection.send_text(message)
                except WebSocketDisconnect:
                    # If the connection fails, mark it for removal
                    connections_to_remove.append(connection)

            # Remove failed connections
            for connection in connections_to_remove:
                self.disconnect(connection, thread_id)

            # Save the message to MongoDB
            self.save_message_to_mongo(thread_id, message)

    def save_message_to_mongo(self, thread_id: str, message: str):
        """Save a message to the MongoDB collection for the given thread."""
        self.threads_collection.update_one(
            {"_id": thread_id},  # Find the thread by its ID
            {"$push": {"messages": message}},  # Add the new message to the 'messages' array
            upsert=True  # Create the thread document if it doesn't exist
        )

    def get_messages_from_thread(self, thread_id: str) -> List[str]:
        """Retrieve all messages for a specific thread from MongoDB."""
        thread = self.threads_collection.find_one({"_id": thread_id})
        if thread and "messages" in thread:
            return thread["messages"]
        else:
            return []
