import json
import os

USER_DATA_FILE = 'user_data.json'

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(user_data, file, indent=4)

def add_user(user_id):
    user_data = load_user_data()
    user_data[user_id] = user_data.get(user_id, 0) + 1
    save_user_data(user_data)

def get_user_count():
    user_data = load_user_data()
    return len(user_data)

def get_all_user_ids():
    user_data = load_user_data()
    return list(user_data.keys())


async def check_subscription(user_id):
    try:
        chat_member = await app.get_chat_member(CHANNEL_ID, user_id)
        return chat_member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except UserNotParticipant:
        return False
    except Exception as e:
        print(f"Error checking subscription: {e}")
        return False

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'count':
            print(f"Total users: {get_user_count()}")
