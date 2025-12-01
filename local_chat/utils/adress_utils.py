from typing import overload

"""
⚠ WARNING: The origin story of my suffering ⚠

This class exists because VSCode lied to me.

I saw this in the type hints for socket.accept():

    def accept() -> tuple[socket, _RetAddress]

And as a certified Python Type Hint Enjoyer™,
I obviously had to recreate `_RetAddress` myself.

Two hours later, after:
 - reading typeshed,
 - learning @overload for no reason,
 - fighting with *args and **kwargs,
 - and questioning the purpose of my existence...

I finally discovered that `_RetAddress` is an INTERNAL TYPE ALIAS
that DOES NOT EXIST AT RUNTIME.

Did I waste my life? Yes 😀.
Did I learn something useful? Debatable.
Will I do it again? Absolutely.

THIS CLASS IS USELESS.
ABANDON ALL HOPE YE WHO ENTER HERE.
And all that just for me to refactor it for a shorter and better version 😭


Author: Myson Dio
License: MIT
Homepage: https://github.com/gtRZync/local-chat
"""

class _RetAddress(tuple[str, int]):
    """
    Brief
    -------------------------
    
    The `_RetAddress` class is just a wrapper type given to an IPv4 adress (too lazy for IPv6)
    
    Args
    -------------------------
    
    address (tuple[str, int]): a tuple that contains the host and port 
    
    host (str): the host ip adress
    
    port (int): the port
    
    Order
    -------------------------
    `adress[0]`: the host ip adress
    
    `adress[1]`: the port
    """
    @overload   
    def __new__(cls, address: tuple[str, int]) -> '_RetAddress': ...
    @overload   
    def __new__(cls, host: str, port: int) -> '_RetAddress': ...
        
    def __new__(cls, *args, **kwargs) -> '_RetAddress | None' :
        #?int, str check maybe
        if len(args) == 1 and isinstance(args[0], tuple):
            host, port = args[0]
        elif len(args) == 2:
            host = args[0]
            port = args[1]
        elif 'address' in kwargs:
            host, port = kwargs.pop('address')
        elif 'host' in kwargs and 'port' in kwargs:
            host, port = kwargs.pop('host'), kwargs.pop('port')
        else:
            raise TypeError("Invalid arguments") 
        return super().__new__(cls, (host, port))
        
    @property
    def host(self) -> str:
        return self[0]
    
    @property
    def port(self) -> int:
        return self[1]
        
    def __repr__(self):
        return f"_RetAddress<host: {self.host}, port: {self.port}>"
        
        
if __name__ == '__main__':
    import random

    def random_ip():
        return ".".join(str(random.randint(0, 255)) for _ in range(4))

    def random_port():
        return random.randint(1024, 65535)  # Avoid well-known ports

    addy0 = _RetAddress(random_ip(), random_port())
    addy1 = _RetAddress(host=random_ip(), port=random_port())
    addy2 = _RetAddress(address=(random_ip(), random_port()))
    addy3 = _RetAddress((random_ip(), random_port()))

    print(addy0)
    print(addy1)
    print(addy2)
    print(addy3)
    print(f"addy0's ip address: {addy0.host}")
    print(f"addy3's port: {addy3.port}")