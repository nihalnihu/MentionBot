from pymongo import MongoClient
import os

MONGO = os.getenv('DB_URL')

client = MongoClient(MONGO)

users = client['main']['users']
groups = client['main']['groups']

def already_db(user_id):
        user = users.find_one({"user_id" : str(user_id)})
        if not user:
            return False
        return True

def already_dbg(chat_id):
        group = groups.find_one({"chat_id" : str(chat_id)})
        if not group:
            return False
        return True

def add_user(user_id):
    in_db = already_db(user_id)
    if in_db:
        return
    return users.insert_one({"user_id": str(user_id)}) 

def remove_user(user_id):
    in_db = already_db(user_id)
    if not in_db:
        return 
    return users.delete_one({"user_id": str(user_id)})
    
def add_group(chat_id, title=None, username=None):
    if already_dbg(chat_id):
        return
    group_data = {"chat_id": str(chat_id)}
    if title:
        group_data["title"] = title
    if username:
        group_data["username"] = username
    return groups.insert_one(group_data)
        
def all_users():
    user = users.find({})
    usrs = len(list(user))
    return usrs

def all_groups():
    group_cursor = groups.find({})
    group_info = []
    for group in group_cursor:
        title = group.get("title", "Unknown")
        username = group.get("username", "None")
        group_info.append(f"{title} - @{username}")
    return group_info
        

def get_all_group_ids():
        return [group['chat_id'] for group in groups.find({})]
