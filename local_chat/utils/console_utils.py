from rich.console import Console
from rich.align import Align
from rich.panel import Panel
from rich import box
import subprocess
import sys
from local_chat.utils.adress_utils import _RetAddress #type: ignore

def clear_sreen():
    if sys.platform == "win32":
        subprocess.run(['cls'], shell=True)
    else:
        subprocess.run(['clear'], shell=True)
        
def print_server_start(stream: Console, host, port):
    msg = f"[bold green]Server started[/bold green]\n[cyan]{host}[/cyan]:[magenta]{port}[/magenta]"
    stream.print(Panel(msg, box=box.ROUNDED, border_style="green", title="SERVER"))
    
def print_server_closed(stream: Console):
    msg = "[bold yellow]Server closed.[/bold yellow]"
    stream.print(Panel(Align.center(msg), box=box.ROUNDED, border_style="green", title="SERVER"))
    
def print_client_connected(stream: Console, address: _RetAddress):
    ip, port = address
    msg = f"[green]{ip}[/green]:[cyan]{port}[/cyan] connected"
    stream.print(Panel(msg, box=box.ROUNDED, border_style="green", title="CLIENT CONNECTED"))
    
def print_client_disconnected(stream: Console, address: _RetAddress):
    ip, port = address
    msg = f"[red]{ip}[/red]:[yellow]{port}[/yellow] disconnected"
    stream.print(Panel(msg, box=box.ROUNDED, border_style="red", title="CLIENT LEFT"))
    
def print_port_in_use(stream: Console, host, port):
    msg = f"[bold red][ERROR] -[/] [bold cyan]Adress: [cyan]{host}[/cyan]:[magenta]{port}[/magenta] already in use.[/bold cyan]"
    stream.print(Panel(Align.center(msg), title="SERVER", border_style='bold red'))
    
def print_incoming_message(stream: Console, address: _RetAddress, text):
    ip, port = address
    msg = (
        f"[bold cyan]From {ip}:{port}[/bold cyan]\n"
        f"[white]{text}[/white]"
    )
    stream.print(Panel(msg, box=box.ROUNDED, border_style="cyan", title="INCOMING"))    
    

def print_keyboard_interrupt(stream: Console):
    msg = "[bold red][CTRL + C detected][/][bold yellow] - Server manually stopped!!![/]"
    stream.print(Panel(Align.center(msg), border_style='yellow', title='WARNING'))
    
def print_os_error(stream: Console, e: OSError):
    errmsg = f"[bold red]{str(e)}[/]" if e else "[bold red][ERROR][/] [bold cyan]An OSError has occured[/]"
    stream.print(Panel(errmsg, title="SERVER", border_style='red'))
    
if __name__ == "__main__":
    console = Console()
    host = '192.168.0.1'
    port = 8080
    address:_RetAddress = _RetAddress('0.0.0.0', port)
    clear_sreen()
    print_client_connected(console, address)
    print_client_disconnected(console, address)
    print_incoming_message(console, address, "Test")
    print_keyboard_interrupt(console)
    print_port_in_use(console, host, port)
    print_server_start(console, host, port)
    # print_os_error(console, )
    print_server_closed(console)