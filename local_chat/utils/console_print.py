from rich.console import Console
from rich.align import Align
from rich.panel import Panel
from rich import box
import subprocess
import sys
from local_chat.utils.adress import Address #type: ignore
import traceback

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
    
def print_client_connected(stream: Console, address: Address):
    ip, port = address
    msg = f"[green]{ip}[/green]:[cyan]{port}[/cyan] connected"
    stream.print(Panel(msg, box=box.ROUNDED, border_style="green", title="CLIENT CONNECTED"))
    
def print_client_disconnected(stream: Console, address: Address):
    ip, port = address
    msg = f"[red]{ip}[/red]:[yellow]{port}[/yellow] disconnected"
    stream.print(Panel(msg, box=box.ROUNDED, border_style="red", title="CLIENT LEFT"))
    
def print_port_in_use(stream: Console, host, port):
    msg = f"[bold red][ERROR] -[/] [bold cyan]Adress: [cyan]{host}[/cyan]:[magenta]{port}[/magenta] already in use.[/bold cyan]"
    stream.print(Panel(Align.center(msg), title="SERVER", border_style='bold red'))
    
def print_incoming_message(stream: Console, address: Address, text):
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
    
    
def _error_panel(title: str, details: str, border="red"):
    console.print(
        Panel(
            f"[bold]{title}[/bold]\n\n[white]{details}[/white]",
            border_style=border,
            box=box.ROUNDED,
        )
    )

def connection_refused(address: Address):
    _error_panel(
        "✗ Connection Refused",
        f"Server at [cyan]{address.host}:{address.port}[/cyan] rejected the connection.\n"
        f"Possible causes:\n"
        f"• Server is offline\n"
        f"• Port is blocked\n"
        f"• Firewall restrictions"
    )

def connection_timeout(address: Address):
    _error_panel(
        "⏳ Connection Timeout",
        f"Timed out while trying to reach [cyan]{address.host}:{address.port}[/cyan].\n"
        f"Possible causes:\n"
        f"• Network lag or no response\n"
        f"• Server is overloaded"
    )

def connection_reset(address: Address):
    _error_panel(
        "⚠️ Connection Reset",
        f"Connection to [cyan]{address.host}:{address.port}[/cyan] was unexpectedly closed.\n"
        f"Possible causes:\n"
        f"• Server crashed or restarted\n"
        f"• Network interruption"
    )

def broken_pipe():
    _error_panel(
        "💥 Broken Pipe",
        "Tried to send data but the connection was no longer valid.\n"
        "Possible causes:\n"
        "• Server closed connection before sending\n"
        "• Network break while sending data"
    )

def exception_occured(err: Exception, show_traceback: bool = False):
    if show_traceback:
        tb = traceback.format_exc()
    else:
        tb = str(err)

    _error_panel(
        "❗ An Exception has occured",
        tb,
        border="magenta"
    )
    
def connection_aborted(address: Address):
    _error_panel(
        "🚫 Connection Aborted",
        f"Connection to [cyan]{address.host}:{address.port}[/cyan] was aborted.\n"
        f"Possible causes:\n"
        f"• Server forcibly closed the connection\n"
        f"• Network interruption\n"
        f"• Protocol violation"
    ) 
    
def connected_to_server(address: Address):
    console.print(
        Panel.fit(
            f"[bold green]✓ Connected to server[/bold green]\n"
            f"[cyan]{address.host}:{address.port}[/cyan]",
            box=box.ROUNDED,
            border_style="green",
        )
    )

def disconnected_from_server(address: Address):
    console.print(
        f"[bold red]- Disconnected from server[/bold red] "
        f"[cyan]{address.host}:{address.port}[/cyan]"
    )
    
if __name__ == "__main__":
    console = Console()
    host = '192.168.0.1'
    port = 8080
    address:Address = Address('0.0.0.0', port)
    clear_sreen()
    print_client_connected(console, address)
    print_client_disconnected(console, address)
    print_incoming_message(console, address, "Test")
    print_keyboard_interrupt(console)
    print_port_in_use(console, host, port)
    print_server_start(console, host, port)
    # print_os_error(console, )
    print_server_closed(console)