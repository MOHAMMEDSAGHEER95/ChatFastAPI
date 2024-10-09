import os

mongo_url = f"mongodb+srv://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@cluster0.w73f6.mongodb.net/?retryWrites=true&w=majority"