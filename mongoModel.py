from bson import ObjectId
from pymongo import MongoClient

client = MongoClient("127.0.0.1", 27017)

chatDB = client.local
collection = chatDB.chatrooms
object_id = ObjectId('6725f94bda41bba50b21d358')