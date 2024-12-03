from pymongo import MongoClient
client = MongoClient()
import os
pw = os.environ['PW']

cnstg = f"mongodb+srv://codyburker:{pw}@cluster0.phkpa.mongodb.net/"
print(f'Read pw: {cnstg}')
client = MongoClient()
db = client.sample_mflix
collection = db.test

new_id = collection.insert_one({
    'hello':'world'
}).insert_id

print(new_id)
