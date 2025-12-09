from rich.console import Console
from local_chat.utils import *
from local_chat.command.auth import get_user_id
from typing import Optional
import threading
import socket
import errno
import sys

# Protocol I chose: 
# AUTH:phone_number:username -> AUTH_OK:user_id or AUTH_FAIL:error
# MSG:receiver_user_id:message_content -> MSG_OK or MSG_FAIL

class Server(socket.socket):
    def __init__(self, host: str = '0.0.0.0', port: int = 5423) -> None:
        clear_sreen()
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        # Store clients by user_id (int)
        self.active_clients: dict[int, socket.socket] = {}
        # Store user info for each client
        self.client_user_info: dict[int, dict] = {}  # user_id -> {name, number}
        self.stream: Console = Console()
        self.HOST: str = host
        self.PORT: int = port
        # messages: conversation_id -> message_id -> message_content
        # conversation_id is a string key from sorted user_ids: "user1_id:user2_id"
        # This structure allows storing messages per conversation for data saving
        self.messages: dict[str, dict[int, str]] = {}
        self.message_counters: dict[str, int] = {}  #?Track message IDs per conversation
        try:
            self.bind((self.HOST, self.PORT))
            print_server_start(self.stream, host, port)
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print_port_in_use(self.stream, self.HOST, self.PORT)
                sys.exit(1)
            else:
                print_os_error(self.stream, e)
                sys.exit(1)
        self.settimeout(1)
        self.listen(5)
        
    def _authenticate_client(self, client_socket: socket.socket) -> Optional[int]:
        """Authenticate client and return user_id if successful, None otherwise."""
        try:
            # Wait for authentication message
            auth_data = client_socket.recv(255).decode('utf-8')
            if not auth_data.startswith("AUTH:"):
                client_socket.sendall(b"AUTH_FAIL:Invalid authentication format")
                return None
            
            # Parse authentication
            parts = auth_data[5:].split(":", 1)  #?Why??? Remove "AUTH:" prefix
            if len(parts) != 2:
                client_socket.sendall(b"AUTH_FAIL:Invalid authentication format")
                return None
            
            phone_number, username = parts
            user_id = get_user_id(phone_number, username)
            
            if user_id is None:
                client_socket.sendall(b"AUTH_FAIL:Invalid credentials")
                return None
            
            # Check if user is already connected
            if user_id in self.active_clients:
                client_socket.sendall(b"AUTH_FAIL:User already connected")
                return None
            
            # Send success response
            client_socket.sendall(f"AUTH_OK:{user_id}".encode('utf-8'))
            
            # Store user info
            from local_chat.command.data_loader import users
            user = next((u for u in users if u.get("id") == user_id), None)
            if user:
                self.client_user_info[user_id] = {
                    "name": user.get("name"),
                    "number": user.get("number")
                }
            
            return user_id
            
        except Exception as e:
            self.stream.print(f"[red]Authentication error: {e}[/red]")
            try:
                client_socket.sendall(b"AUTH_FAIL:Server error during authentication")
            except:
                pass
            return None
    
    def _get_conversation_id(self, user1_id: int, user2_id: int) -> str:
        """Generate a consistent conversation ID from two user IDs."""
        sorted_ids = tuple(sorted([user1_id, user2_id]))
        return f"{sorted_ids[0]}:{sorted_ids[1]}"
    
    def _store_message(self, sender_id: int, receiver_id: int, message_content: str):
        """Store message in messages dict."""
        conv_id = self._get_conversation_id(sender_id, receiver_id)
        
        if conv_id not in self.messages:
            self.messages[conv_id] = {}
            self.message_counters[conv_id] = 0
        
        message_id = self.message_counters[conv_id]
        self.messages[conv_id][message_id] = message_content
        self.message_counters[conv_id] += 1
        
    def handle_client(self, client_socket: socket.socket, client_address: Address, user_id: int):
        """Handle client communication after authentication."""
        while True:
            try:
                response = client_socket.recv(255)
                if response == b'':
                    self._disconnect_client(user_id, client_address)
                    break
                
                message_data = response.decode('utf-8')
                
                # Handle message protocol: MSG:receiver_user_id:message_content
                if message_data.startswith("MSG:"):
                    parts = message_data[4:].split(":", 1)  # Remove "MSG:" prefix
                    if len(parts) != 2:
                        client_socket.sendall(b"MSG_FAIL:Invalid message format")
                        continue
                    
                    try:
                        receiver_id = int(parts[0])
                        message_content = parts[1]
                        
                        # Store message
                        self._store_message(user_id, receiver_id, message_content)
                        
                        # Relay to receiver if online
                        if receiver_id in self.active_clients:
                            receiver_socket = self.active_clients[receiver_id]
                            sender_name = self.client_user_info.get(user_id, {}).get("name", "Unknown")
                            formatted_message = f"MSG:{user_id}:{sender_name}:{message_content}"
                            receiver_socket.sendall(formatted_message.encode('utf-8'))
                            client_socket.sendall(b"MSG_OK")
                        else:
                            client_socket.sendall(b"MSG_FAIL:Receiver not online")
                            
                    except ValueError:
                        client_socket.sendall(b"MSG_FAIL:Invalid receiver ID")
                    except Exception as e:
                        self.stream.print(f"[red]Error relaying message: {e}[/red]")
                        client_socket.sendall(b"MSG_FAIL:Server error")
                else:
                    client_socket.sendall(b"MSG_FAIL:Unknown message format")
                
            except ConnectionResetError:
                self._disconnect_client(user_id, client_address)
                break
            except Exception as e:
                self.stream.print(f"[red]Error handling client {user_id}: {e}[/red]")
                self._disconnect_client(user_id, client_address)
                break
    
    def _disconnect_client(self, user_id: int, client_address: Address):
        """Handle client disconnection."""
        if user_id in self.active_clients:
            try:
                self.active_clients[user_id].close()
            except:
                pass
            del self.active_clients[user_id]
        if user_id in self.client_user_info:
            del self.client_user_info[user_id]
        print_client_disconnected(self.stream, client_address)
    
    def run(self):
        try:
            while True:
                try:
                    client, address = self.accept()
                    print_client_connected(self.stream, Address(address))
                    
                    # Authenticate client
                    user_id = self._authenticate_client(client)
                    if user_id is None:
                        client.close()
                        continue
                    
                    # Add to active clients
                    self.active_clients[user_id] = client
                    user_name = self.client_user_info.get(user_id, {}).get("name", "Unknown")
                    self.stream.print(f"[green]User {user_name} (ID: {user_id}) authenticated[/green]")
                    
                    # Start handling client in separate thread
                    threading.Thread(
                        target=self.handle_client, 
                        args=(client, Address(address), user_id), 
                        daemon=True
                    ).start()
                    
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            print_keyboard_interrupt(self.stream)
        finally:
            self.close()
            print_server_closed(self.stream)

if __name__ == "__main__":
    server = Server()
    server.run()