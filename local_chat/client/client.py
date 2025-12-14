import socket
import sys
from local_chat.utils.adress import Address 
from local_chat.utils.console_print import (connection_refused, connection_aborted, connection_timeout, disconnected_from_server,
                                            connection_reset, broken_pipe, exception_occured, connected_to_server)
import threading
from typing import Optional, Callable, Any
import queue

class Client(socket.socket):
    def __init__(self, phone_number: str, username: str, address: Address = Address(host='localhost', port=5423)):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.phone_number = phone_number
        self.username = username
        self.user_id: int | None = None
        self.serv_adress = address
        self.gui_event_queue = queue.Queue()
        self.message_callback: Optional[Callable[[int, str, str], Any]] = None  # (sender_id, sender_name, message)
        self.establish_connection(address)
        
    def set_message_callback(self, callback: Callable[[int, str, str], Any]):
        """Set callback function to handle incoming messages.
        
        Callback signature: 
        ------------------
        callback(sender_id: int, sender_name: str, message: str)
        
        callback args:
        -------------
        sender_id (int)
        
        sender_name (str)
        
        message (str)
        """
        self.message_callback = callback
        
    def send_message(self, receiver_user_id: int, message: str) -> bool:
        if self.user_id is None:
            print("Error: Not authenticated. Cannot send message.")
            return False
    
        old_timeout = self.gettimeout()
        try:
            # Temporary timeout
            self.settimeout(5)
            
            message_data = f"MSG:{receiver_user_id}:{message}"
            self.sendall(message_data.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
        finally:
            try:
                self.settimeout(old_timeout)
            except Exception:
                pass

    
    def listen_for_messages(self):
        """Listen for incoming messages from the server."""
        while True:
            try:
                response = self.recv(255)
                if response == b'':
                    break
                
                message_data = response.decode('utf-8')
                
                # Handle message protocol: MSG:sender_id:sender_name:message_content
                if message_data.startswith("MSG:"):
                    parts = message_data[4:].split(":", 2)  # Remove "MSG:" prefix
                    if len(parts) == 3:
                        sender_id = int(parts[0])
                        sender_name = parts[1]
                        message_content = parts[2]
                        
                        # Note: Callback should handle thread safety if updating UI, that's why i'm using ctk's after method thank God lol
                        if self.message_callback:
                            #just realised i'm sending some useless data, 'the name'
                            self.message_callback(sender_id, sender_name, message_content)
                        else:
                            print(f"[{sender_name}]: {message_content}")
                elif message_data.startswith("EVENT:"):
                   parts = message_data[6:].split(":")
                   if len(parts) == 1:
                       event_type = parts[0]
                       self.gui_event_queue.put({'type' : event_type})
                   elif len(parts) == 3:
                       event_type = parts[0]
                       user_id = parts[1]
                       status = parts[2]
                       self.gui_event_queue.put(
                           {
                               'type': event_type,
                               'user_id' : int(user_id),
                               'status' : status
                           }
                       )
                        
                       
                else:
                    print(f"Received: {message_data}")
            except socket.timeout:
                pass
            except ConnectionResetError as e:
                print(f"Connection reset: {e}")
                break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break
        
        # Close socket when loop exits
        try:
            self.close()
            disconnected_from_server(self.serv_adress)
        except Exception:
            pass
                
    def _authenticate(self) -> bool:
        """Authenticate with the server using phone number and username."""
        try:
            # Send authentication: AUTH:phone_number:username
            auth_data = f"AUTH:{self.phone_number}:{self.username}"
            self.sendall(auth_data.encode('utf-8'))
            
            # Wait for response
            response = self.recv(255).decode('utf-8')
            
            if response.startswith("AUTH_OK:"):
                # Extract user_id from response
                self.user_id = int(response.split(":")[1])
                print(f"Authentication successful! User ID: {self.user_id}")
                return True
            else:
                error_msg = response.split(":", 1)[1] if ":" in response else response
                print(f"Authentication failed: {error_msg}")
                return False
                
        except Exception as e:
            print(f"Error during authentication: {e}")
            return False
                
    def establish_connection(self, address: Address):
        """Establish connection to server and authenticate."""
        try:
            # Set socket timeout to prevent indefinite blocking
            self.settimeout(10)  # 10 second timeout for connection operations
            self.connect(address)
            connected_to_server(address)
            
            # Authenticate
            if not self._authenticate():
                self.close()
                sys.exit(1)
            
            # Set longer timeout for message operations
            self.settimeout(None)  # No timeout for listening (blocking is expected)
            
            # Start listening for messages
            threading.Thread(target=self.listen_for_messages, daemon=True).start()

        except ConnectionRefusedError:
            connection_refused(address)
            sys.exit(1)
            
        except ConnectionAbortedError:
            connection_aborted(address)
            sys.exit(1)

        except TimeoutError:
            connection_timeout(address)
            sys.exit(1)

        except ConnectionResetError:
            connection_reset(address)
            sys.exit(1)

        except BrokenPipeError:
            broken_pipe()
            sys.exit(1)

        except Exception as e:
            exception_occured(e, show_traceback=True)
            sys.exit(1)
            
        #TODO: add finally that can trigger a gui_event to reconnect
        
        
        