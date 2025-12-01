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
    def __init__(self, address: tuple[str, int]) -> None: ...
    @overload
    def __init__(self, host: str, port: int) -> None: ...
        
    def __init__(self, *args, **kwargs) -> None:
        self.host: str
        self.port: int
    @overload   
    def __new__(cls, address: tuple[str, int]) -> '_RetAddress': ...
    @overload   
    def __new__(cls, host: str, port: int) -> '_RetAddress': ...
        
    def __new__(cls, *args, **kwargs) -> '_RetAddress | None' :
        #?int, str check maybe
        if args:
            if len(args) == 1 and isinstance(args[0], tuple):
                cls.host = args[0][0]
                cls.port = args[0][1]
                return super().__new__(cls)
            elif len(args) == 2:
                cls.host = args[0]
                cls.port = args[1]
                return super().__new__(cls)
        elif kwargs:
            if len(kwargs) == 1 and isinstance(list(kwargs.items())[0][1], tuple):
                if 'address' in kwargs:
                    cls.host, cls.port = kwargs.pop('address')
                else:
                    raise ValueError(f'"{list(kwargs.keys())[0]}" is not a supported argument.')
                return super().__new__(cls)
            elif len(kwargs) == 2:
                if 'host' in kwargs:
                    cls.host = kwargs.pop('host')
                if 'port' in kwargs:
                    cls.port = kwargs.pop('port')
                unexpected_kwargs = set(kwargs) - {'host', 'port'}
                if unexpected_kwargs:
                    raise ValueError(f"Unexpected argument(s) passed: {', '.join(unexpected_kwargs)}")
                return super().__new__(cls)
        else:
            raise TypeError("Invalid arguments")
        
    def __repr__(self):
        return f"_RetAddress<host: {self.host}, port: {self.port}>"
        
        
if __name__ == '__main__':
    addy0 = _RetAddress('192.168.0.1', 8080)
    addy1 = _RetAddress(host='192.168.0.1', port=8080)
    addy2 = _RetAddress(address=('192.168.0.1', 8080))
    addy3 = _RetAddress(('192.168.0.1', 8080))
    print(addy0)
    print(addy1)
    print(addy2)
    print(addy3)
    print(f"ip address: {addy0.host}")
    print(f"port: {addy3.port}")