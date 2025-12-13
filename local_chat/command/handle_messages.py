"""
Message handling and persistence functions.
Handles saving messages to database and managing conversations.
"""
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class CreationStatus:
    created: bool
    existing: bool
    op_failed: bool


def save_message_to_conversation(
    sender_id: int,
    receiver_id: int,
    message_content: str,
    timestamp: str | None = None
) -> bool:
    """
    Save a message to the conversation between two users.
    Creates a new conversation if it doesn't exist.

    Args:
        sender_id: ID of the user sending the message
        receiver_id: ID of the user receiving the message
        message_content: The message text
        timestamp: Optional timestamp string. If None, generates current UTC timestamp.

    Returns:
        True if message was saved successfully, False otherwise.
    """
    from local_chat.command.data_loader import (
        fetch_users_and_conversations,
        get_conversations_between_users,
        save_database,
    )
    try:
        users, conversations = fetch_users_and_conversations()

        # Find or create conversation
        conversation = get_conversations_between_users(sender_id, receiver_id)

        if timestamp is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        message = {
            "sender_id": sender_id,
            "content": message_content,
            "timestamp": timestamp
        }

        if conversation is None:
            conversation = create_conversation(sender_id, receiver_id)
            if conversation is None:
                return False

        for conv in conversations:
            if conv['id'] == conversation['id']:
                conv['messages'].append(message)

        return save_database(users, conversations)

    except Exception as e:
        print(f"Error saving message to conversation: {e}")
        return False


def create_conversation(user1_id: int, user2_id: int) -> dict | None:
    """
    Create a new conversation between two users.

    Args:
        user1_id: First user's ID
        user2_id: Second user's ID

    Returns:
        The created conversation dict, or None if creation failed.
    """
    from local_chat.command.data_loader import (
        fetch_users_and_conversations,
        get_conversations_between_users,
        save_database,
    )
    try:
        users, conversations = fetch_users_and_conversations()

        existing = get_conversations_between_users(user1_id, user2_id)
        if existing:
            return existing

        max_id = max([conv.get("id", 0) for conv in conversations], default=0)
        new_conv_id = max_id + 1

        new_conversation = {
            "id": new_conv_id,
            "user_ids": [user1_id, user2_id],
            "messages": []
        }

        conversations.append(new_conversation)

        if save_database(users, conversations):
            return new_conversation
        else:
            # Rollback if save failed
            conversations.pop()
            return None

    except Exception as e:
        print(f"Error creating conversation: {e}")
        return None


def ensure_conversation_exists(user1_id: int, user2_id: int) -> CreationStatus:
    """
    Ensure a conversation exists between two users.
    Creates it if it doesn't exist.

    Args:
        user1_id: First user's ID
        user2_id: Second user's ID

    Returns:
        CreationStatus: An object describing the outcome of the creation attempt, containing:
            created (bool): True if a new item was successfully created.
            existing (bool): True if the item already existed and no new creation occurred.
            op_failed (bool): True if the operation could not be completed due to an error.

    """
    from local_chat.command.data_loader import (
        fetch_users_and_conversations,
        save_database,
    )
    users, conversations = fetch_users_and_conversations()

    target_set = {user1_id, user2_id}
    matches = [
        conv for conv in conversations
        if set(conv.get("user_ids", [])) == target_set
    ]
    if len(matches) > 1:
        base = matches[0]
        for dup in matches[1:]:
            base["messages"].extend(dup.get("messages", []))
            try:
                conversations.remove(dup)
            except ValueError:
                pass

        save_database(users, conversations)
        return CreationStatus(created=False,existing=True,op_failed=False)

    if len(matches) == 1:
        return CreationStatus(created=False,existing=True,op_failed=False)

    # None found -> create one
    conversation = create_conversation(user1_id, user2_id)

    return CreationStatus(
        created=conversation is not None,
        existing=False,
        op_failed=conversation is None
    )


def create_conversations_for_connected_user(
    new_user_id: int,
    existing_user_ids: list[int]
) -> CreationStatus:
    """
    Create conversations between a newly connected user and all existing connected users.
    This ensures they appear in each other's contact lists.

    Args:
        new_user_id: ID of the newly connected user
        existing_user_ids: List of user IDs already connected to the server

    Returns:
        CreationStatus: An object describing the outcome of the creation attempt, containing:
            created (bool): True if a new item was successfully created.
            existing (bool): True if the item already existed and no new creation occurred.
            op_failed (bool): True if the operation could not be completed due to an error.
    """
    try:
        print(f"existing_user_ids: {existing_user_ids}")
        status = CreationStatus(created=False, existing=True, op_failed=False)
        for existing_user_id in existing_user_ids:
            status = ensure_conversation_exists(new_user_id, existing_user_id)

        return status
    except Exception as e:
        print(f"Error creating conversations for connected user: {e}")
        return CreationStatus(created=False, existing=False, op_failed=True)
