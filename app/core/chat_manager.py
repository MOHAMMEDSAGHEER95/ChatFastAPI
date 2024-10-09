# app/core/chat_manager.py

from typing import List, Dict
from uuid import uuid4


class ChatManager:
    def __init__(self):
        # Dictionary to store messages in each thread
        self.threads: Dict[str, List[str]] = {}

    def create_thread(self) -> str:
        """Create a new thread and return its unique thread_id"""
        thread_id = str(uuid4())  # Generate a unique ID for the thread
        self.threads[thread_id] = []  # Initialize the thread with an empty message list
        return thread_id

    def add_message_to_thread(self, thread_id: str, message: str):
        """Add a message to an existing thread"""
        if thread_id in self.threads:
            self.threads[thread_id].append(message)
        else:
            raise ValueError(f"Thread {thread_id} does not exist")

    def get_messages(self, thread_id: str) -> List[str]:
        """Get all messages from a thread"""
        if thread_id in self.threads:
            return self.threads[thread_id]
        else:
            raise ValueError(f"Thread {thread_id} does not exist")
