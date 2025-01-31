from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

# Connect to MongoDB
client = MongoClient(MONGODB_URI, tls=True, tlsAllowInvalidCertificates=True)
db = client["telegram_bot"]

# Collections
users_collection = db["users"]
chat_history_collection = db["chat_history"]
file_metadata_collection = db["file_metadata"]