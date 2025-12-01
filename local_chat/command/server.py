from rich.console import Console
from local_chat.utils import *
from typing import Literal
import threading
import socket
import errno
import sys

#for data saving, i'm thinking force login or sumthin so the data will be associated by account

class Server(socket.socket):
    def __init__(self, host: str = '0.0.0.0', port: int = 8080) -> None:
        clear_sreen()
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.active_clients: dict[str, socket.socket] = {}
        self.stream: Console = Console()
        self.HOST: str = host
        self.PORT: int = port
        self.USER_A: Literal["user_a"] = "user_a"
        self.USER_B: Literal["user_b"] = "user_b"
        try:
            self.bind((self.HOST, self.PORT))
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print_port_in_use(self.stream, self.HOST, self.PORT)
                sys.exit(1)
            else:
                print_os_error(self.stream, e)
                sys.exit(1)
        self.settimeout(1)
        self.listen(5)
        
    def handle_client(self, client_socket: socket.socket, client_address: _RetAddress):
        while True:
            try:
                response = client_socket.recv(255)
                if response == b'':
                    print_client_disconnected(self.stream, client_address)
                    break
                sender: str = "TODO: add a way to get sender ID"
                self.relay_messages(sender, response)
                
            except ConnectionResetError as e:
                print(e) #TODO: make it better
            except Exception as e:
                print(e) #TODO: make it better
            finally:
                client_socket.close()
    
    def relay_messages(self, sender: str, message: bytes): #?Should i create a Message class to handle emojies, stickers, images???? (if yes image first) 
        for id in self.active_clients:
            if id is not sender:
                client = self.active_clients.get(id)
                if client is not None:
                    client.sendall(message)
    
    def run(self):
        try:
            while True:
                try:
                    client, address = self.accept()
                    print_client_connected(self.stream, _RetAddress(address))
                    if self.USER_A in self.active_clients: #TODO: this is bad change it bromoto ✌🏻😭
                        self.active_clients[self.USER_B] = client
                    threading.Thread(target=self.handle_client, args=(client, _RetAddress(address)), daemon=True).start()
                except socket.timeout:
                    pass
        except KeyboardInterrupt:
            print_keyboard_interrupt(self.stream)
        finally:
            self.close()
            print_server_closed(self.stream)

def run_server(address: _RetAddress = _RetAddress(host= '0.0.0.0', port= 9999)):
    host = address.host
    port = address.port
    console = Console()
    clear_sreen()
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((host, port))
    except OSError as e:
        if e.errno == errno.EADDRINUSE:
            print_port_in_use(console, host, port)
            sys.exit(1)
        else:
            print_os_error(console, e)
            sys.exit(1)
    print_server_start(console, host, port)

    server.settimeout(1)
    server.listen(5)

    try:
        while True:
            try:
                client, address = server.accept()
                print_client_connected(console, address)
                while True:
                    response = client.recv(255)
                    if response == b'':
                        client.close()
                        print_client_disconnected(console, address)
                        break            
                    print_incoming_message(console, address, response.decode())
            except socket.timeout:
                pass
            except ConnectionResetError:
                if 'address' in locals():
                    print_client_disconnected(console, address) #type: ignore
            finally:    
                if 'client' in locals():
                    client.close()#type: ignore
    except KeyboardInterrupt:
        print_keyboard_interrupt(console)
    finally:
        server.close()
        print_server_closed(console)
        
if __name__ == "__main__":
    run_server()