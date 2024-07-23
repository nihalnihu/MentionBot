from pymongo import MongoClient
import os

# Environment variable for MongoDB URL
MONGO = os.getenv('DB_URL', 'mongodb://localhost:27017')  # Default to localhost if not set

# Initialize MongoDB client
client = MongoClient(MONGO)

# Define MongoDB collections
users = client['main']['users']
groups = client['main']['groups']

def already_db(user_id):
    """
    Check if a user already exists in the database.
    """
    user = users.find_one({"user_id": str(user_id)})
    return user is not None

def already_dbg(chat_id):
    """
    Check if a group already exists in the database.
    """
    group = groups.find_one({"chat_id": str(chat_id)})
    return group is not None

def add_user(user_id):
    """
    Add a new user to the database if they don't already exist.
    """
    if not already_db(user_id):
        return users.insert_one({"user_id": str(user_id)})

def remove_user(user_id):
    """
    Remove a user from the database if they exist.
    """
    if already_db(user_id):
        return users.delete_one({"user_id": str(user_id)})

def add_group(chat_id, title=None, username=None):
    """
    Add a new group to the database with optional title and username.
    """
    if not already_dbg(chat_id):
        group_data = {"chat_id": str(chat_id)}
        if title:
            group_data["title"] = title
        if username:
            group_data["username"] = username
        return groups.insert_one(group_data)

def all_users():
    """
    Return the total number of users in the database.
    """
    return users.count_documents({})

def all_groups():
    """
    Return a list of all groups with their title and username.
    """
    group_cursor = groups.find({})
    group_info = []
    for group in group_cursor:
        title = group.get("title", "Unknown")
        username = group.get("username", "None")
        group_info.append(f"{title} - @{username}")
    return group_info

def get_all_group_ids():
    """
    Return a list of all group IDs.
    """
    return [group['chat_id'] for group in groups.find({})]
