import json
from typing import Optional
from local_chat.config.path import DATABASE_DIR, DEFAULT_DATABASE_STRUCTURE
from rich import print
from rich.panel import Panel

_User = dict
_Users = list[dict]
_Conversation = dict
_Conversations = list[dict]

def __get_users_and_conversations(data, /) -> tuple[_Users, _Conversations]:
    return data.get('users', []), data.get('conversations', [])

def load_database():
    try:
        if not DATABASE_DIR.exists() or DATABASE_DIR.stat().st_size == 0:
            DATABASE_DIR.parent.mkdir(exist_ok=True)
            with open(DATABASE_DIR, 'w') as json_file:
                json.dump(DEFAULT_DATABASE_STRUCTURE, json_file, indent=4)
                return DEFAULT_DATABASE_STRUCTURE
                
        with open(DATABASE_DIR) as database:
            return json.load(database)
    except FileNotFoundError:
        print(Panel(f"The file '{DATABASE_DIR}' was not found.", title="[red]File Not Found[/red]", style="red"))
    except json.JSONDecodeError:
        print(Panel(f"Failed to decode JSON from '{DATABASE_DIR}'.", title="[red]JSON Error[/red]", style="red"))
    except Exception as e:
        print(Panel(f"{e}", title="[red]Unexpected Error[/red]", style="red"))
        
def save_database(users: _Users, conversations: _Conversations, /) -> bool:
    """
    Save users and conversations back to the database file.
    """
    try:
        data = {
            "users": users,
            "conversations": conversations
        }
        with open(DATABASE_DIR, 'w') as json_file:
            json.dump(data, json_file, indent=2)
        return True
    except Exception as e:
        print(f"Error saving database: {e}") #TODO: use rich print, fn in console_utils.py
        return False
        
    
def fetch_users_and_conversations() -> tuple[_Users, _Conversations]:
    """Query database and returns users and conversations."""
    data = load_database()
    return __get_users_and_conversations(data)

def get_contacts_for_user(current_user_id: int) -> _Users:
    contacts = []
    users, conversations = fetch_users_and_conversations()
    for conversation in conversations:
        if current_user_id in conversation['user_ids']:
            other_user_id = [id for id in conversation['user_ids'] if id is not current_user_id][0]
            other_user = find_user_by_id(other_user_id, users)
            
            if other_user:
                contact_info = {
                    'user_id': other_user_id,
                    'name' : other_user['name'],
                    'number': other_user['number'],
                    'photo_path': None ,#not supported yet
                    'status': 'offline', #TODO: add status check (from server)
                    'conversation_id': conversation['id'],
                    'last_message': get_last_message(conversation),
                    'last_message_time': get_last_message_time(conversation)
                }
                contacts.append(contact_info)
                
    return remove_duplicates_by_user_id(contacts)                 
                
                
def find_user_by_id(user_id: int , users: _Users, /) -> Optional[_User]: 
    for user in users:
        if user['id'] == user_id:
            return user
    return None
        
def get_last_message(conversation: _Conversation, /) -> dict | None: 
    if conversation['messages'] == []:
        return None
    last_msg = conversation['messages'][-1]
    return last_msg
    
def get_last_message_time(conversation: _Conversation, /) -> str | None: 
    last_msg = get_last_message(conversation)
    if last_msg:
        return last_msg['timestamp']
    return None
    
def remove_duplicates_by_user_id(contacts: _Users) -> list:
    seen_user_ids = {}
    
    for contact in contacts:
        user_id = contact['user_id']
        if user_id not in seen_user_ids:
            seen_user_ids[user_id] = contact
        else:
            if contact['last_message_time']:
                if contact['last_message_time'] > seen_user_ids[user_id]['last_message_time']:
                    seen_user_ids[user_id] = contact  
    return list(seen_user_ids.values())
    
def get_conversations_between_users(user1_id: int, user2_id: int) ->Optional[_Conversation] :
    _, conversations = fetch_users_and_conversations()
    
    for conversation in conversations:
        user_ids_set = set(conversation['user_ids'])
        target_set = {user1_id, user2_id}
        
        if user_ids_set == target_set:
            return conversation
    return None
    
def load_conversation_messages(conversation: _Conversation, /) -> list[dict]:
    if conversation is None:
        return []
    return conversation['messages']
    

    
