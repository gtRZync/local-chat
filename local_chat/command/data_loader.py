import json
from local_chat.config.path import DATABASE_DIR
from rich import print
from rich.panel import Panel

_Users = list[dict]
_Conversations = list[dict]

users = []
conversations = []

def get_users_and_conversations(data, /) -> tuple[_Users, _Conversations]:
    return data.get('users', []), data.get('conversations', [])

def load_database():
    try:
        with open(DATABASE_DIR) as json_file:
            json_obj = json_file.read()
            data = json.loads(json_obj)
            return data
    except FileNotFoundError:
        print(Panel(f"The file '{DATABASE_DIR}' was not found.", title="[red]File Not Found[/red]", style="red"))
    except json.JSONDecodeError:
        print(Panel(f"Failed to decode JSON from '{DATABASE_DIR}'.", title="[red]JSON Error[/red]", style="red"))
    except Exception as e:
        print(Panel(f"{e}", title="[red]Unexpected Error[/red]", style="red"))

    
def init_data():
    """Initialize global users and conversations."""
    global users, conversations
    data = load_database()
    users, conversations = get_users_and_conversations(data)
    
init_data()