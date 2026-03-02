import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    DB_NAME = "github_webhooks"
    COLLECTION_NAME = "events"
    GITHUB_SECRET = os.getenv("GITHUB_SECRET")