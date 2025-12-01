import socket
from local_chat.utils.adress_utils import _RetAddress #type:ignore

class Client(socket.socket):
    def __init__(self):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        
    def send_message(self, message: str):
        self.sendall(message.encode())
    
    def listen_for_messages(self):
        while True:
            try:
                response = self.recv(255)
                if response == b'':
                    break
                sender: str = "TODO: add a way to get sender ID"
                #?maybe message should not simply be decoded but parsed or like a message class 
                #TODO: display the message
            except ConnectionResetError as e:
                print(e) #TODO: make it better
            except Exception as e:
                print(e) #TODO: make it better
            finally:
                self.close()
    def establish_connection(self, address: _RetAddress):
        pass
        
        
        