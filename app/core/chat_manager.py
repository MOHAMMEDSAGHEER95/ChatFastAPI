# app/core/chat_manager.py
import os
from uuid import uuid4
from pymongo import MongoClient
from typing import List, Dict

from app.core.config import mongo_url
from app.openai.client import OpenAIClientHelper


class ChatManager:
    def __init__(self):
        # Connect to MongoDB Atlas
        self.client = MongoClient(
            mongo_url
        )
        self.db = self.client["chat_db"]  # The database name is "chat_db"
        self.threads_collection = self.db["threads"]  # The collection for threads

    def create_thread(self) -> str:
        """Create a new thread and return its unique thread_id"""
        openai_client = OpenAIClientHelper()
        thread = openai_client.create_thread()

        # Insert the new thread into MongoDB
        self.threads_collection.insert_one({
            "_id": thread,
            "messages": []  # Initialize the thread with an empty message list
        })

        return thread

    def get_messages(self, thread_id: str) -> List[str]:
        """Get all messages from a thread"""
        # Find the thread in MongoDB by its ID
        thread = self.threads_collection.find_one({"_id": thread_id})

        if thread:
            return thread["messages"]  # Return the list of messages
        else:
            raise ValueError(f"Thread {thread_id} does not exist")
