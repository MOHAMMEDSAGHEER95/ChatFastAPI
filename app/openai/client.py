import os

from openai import OpenAI


class OpenAIClientHelper:
    client = None

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPEN_AI_KEY'))

    def get_assistants(self):
        my_assistants = self.client.beta.assistants.list( order="desc", limit=20)
        print(my_assistants)

    def get_messages(self, thread_id: str):
        thread_messages = self.client.beta.threads.messages.list(thread_id)
        return thread_messages.data

    def add_message(self, thread_id: str, message: str):
        thread_message = self.client.beta.threads.messages.create(
            thread_id,
            role="user",
            content=message,
        )

    def run_thread(self, thread_id: str, assistant: str):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant,
            stream=True
        )
        for event in run:
            print(event)

    def create_thread(self):
        empty_thread = self.client.beta.threads.create()
        return empty_thread.id
