from pymongo import MongoClient

MONGO = "mongodb+srv://Nk:nk@cluster0.chzrcq5.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(MONGO)

users = client['main']['M_users']
groups = client['main']['M_groups']

def already_db(user_id):
        user = M_users.find_one({"user_id" : str(user_id)})
        if not user:
            return False
        return True

def already_dbg(chat_id):
        group = M_groups.find_one({"chat_id" : str(chat_id)})
        if not group:
            return False
        return True

def add_user(user_id):
    in_db = already_db(user_id)
    if in_db:
        return
    return M_users.insert_one({"user_id": str(user_id)}) 

def remove_user(user_id):
    in_db = already_db(user_id)
    if not in_db:
        return 
    return M_users.delete_one({"user_id": str(user_id)})
    
def add_group(chat_id):
    in_db = already_dbg(chat_id)
    if in_db:
        return
    return M_groups.insert_one({"chat_id": str(chat_id)})

def all_users():
    user = M_users.find({})
    usrs = len(list(user))
    return usrs

def all_groups():
    group = M_groups.find({})
    grps = len(list(group))
    return grps
