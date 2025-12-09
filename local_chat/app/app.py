import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from PIL import Image, ImageTk
from local_chat.utils import Vector2i
from local_chat.utils import TimeUpdatableMixin
from local_chat.gui.widgets import AppIcon, StatusBar
from local_chat.config import ASSETS_DIR, FONT_DIR
from local_chat.gui.views import LoginView, ChatListView, ConversationView
from local_chat.client import Client

class Phone(ctk.CTk, TimeUpdatableMixin):
    def __init__(self, width: int = 421, height: int = 820):
        super().__init__()
        self.title('Phone')
        self.geometry(self.__scale_size(width, height))
        self.resizable(False, False)
        ctk.FontManager.load_font(str(FONT_DIR / 'SF-Pro-Display-Regular.otf'))
        ctk.FontManager.load_font(str(FONT_DIR / 'SF-Pro-Display-Bold.otf'))
        ctk.FontManager.load_font(str(FONT_DIR / 'SF-Pro-Text-Bold.otf'))
        ctk.FontManager.load_font(str(FONT_DIR / 'SF-Pro-Text-Regular.otf'))
        ctk.set_appearance_mode('light')
        bg = Image.open(ASSETS_DIR / 'background/lord.jpg').resize((421, 820))
        self.__bg_tk = ImageTk.PhotoImage(bg)

        icon = Image.open(ASSETS_DIR / 'icon/MissingTexture.png').resize((80, 80))
        self.__icon_tk = ImageTk.PhotoImage(icon)
        
        self.canvas = ctk.CTkCanvas(self, width=bg.width, height=bg.height, bd=0, highlightthickness=0)
        self.canvas.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)

        self.canvas.create_image(0, 0, anchor='nw', image=self.__bg_tk)
        x = (self.__bg_tk.width() - self.__icon_tk.width()) // 2
        y = (self.__bg_tk.height() - self.__icon_tk.height()) // 2
        
        #TODO: add snap to grid and clamping
        font = ctk.CTkFont(family='SF Pro Text', size=20, weight='normal')
        self._app_icon = AppIcon(self.canvas, self.__icon_tk, Vector2i(x, y), font=font, app_name='Chat')
        self._status_bar = StatusBar(self.canvas, bg.width)
        
        self.__clock_id = self.canvas.create_text(
            bg.width //2,
            bg.height / 4,
            text=self.get_time_text(),
            font=ctk.CTkFont(family='SF Pro Text', size=60, weight='bold'),
            fill='white',
            anchor='center'
        )

        date = datetime.now().strftime('%a, %B %#d')
        self.__date_id = self.canvas.create_text(
            bg.width //2,
            (bg.height / 4) + 35,
            text=date,
            font=ctk.CTkFont(family='SF Pro Text', size=15, weight='normal'),
            fill='white',
            anchor='center'
        )
        #not updating the day since a day last 24h and polling for 24 hours feel like useless background load so yeah as the date won't
        #change that often, i ain't doing it
        self.canvas.after(200, self.update_time)
        self.bind('<Key>',self.__close_app)
        self.canvas.tag_bind(self._app_icon.icon_id, '<ButtonRelease-1>', self.__launch_app, add='+')
        
        self.current_view: tk.Widget| None = self.canvas
        self.previous_view: tk.Widget| None = None
        
        #different views bromoto 🦧
        self.loginView = LoginView(self, self.__return)
        self.chatListView = ChatListView(self, lambda: self.__return(self.canvas))
        self.client: Client | None = None  # Will be initialized after login
        self.conversationView: ConversationView | None = None  # Will be created when needed
        
        # Initialize client after successful login
        self.loginView.on_login(self.__on_login_success)
        
    def show_view(self, view: tk.Widget):
        if self.current_view:
            self.previous_view = self.current_view
            self.current_view.pack_forget()
            
        self.current_view = view
        self.current_view.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)
        self.current_view.focus_set()
     
    @property   
    def time_id(self) -> int:
        return self.__clock_id
        
    def __close_app(self, event: tk.Event):
        if event.keysym.lower() == 'escape':
            if event.widget is self.canvas or event.widget is self:
                self.quit()

    def __scale_size(self, width: int, height: int, /) -> str:
        scale = self._get_window_scaling() 
        scaled_x = int(width / scale)
        scaled_y = int(height / scale)
        return f'{scaled_x}x{scaled_y}'
    
    def __launch_app(self, event: tk.Event):
        if self._app_icon.should_launch_app and not self.loginView.logged_in:
            self.show_view(self.loginView)
        elif self._app_icon.should_launch_app and self.loginView.logged_in:
            self.show_view(self.chatListView)
            
    def __on_login_success(self):
        """Initialize client connection after successful login."""
        import threading
        from local_chat.utils.adress import Address
        
        # Get credentials from login view
        phone_number = self.loginView.phone_number
        username = self.loginView.username
        
        # Show connecting status (optional - might want to add a loading indicator)
        # Navigate to chat list first
        self.show_view(self.chatListView)
        
        # Initialize client in a separate thread to avoid blocking UI
        def connect_client():
            try:
                # Initialize client with credentials (this will block, but in background thread)
                client = Client(
                    phone_number=phone_number,
                    username=username,
                    address=Address(host='localhost', port=5423)
                )
                
                # Update client on main thread using after()
                self.after(0, lambda: self._on_client_connected(client))
                
            except Exception as e:
                # Handle error on main thread
                self.after(0, lambda: self._on_client_connection_error(str(e)))
        
        # Start connection in background thread
        threading.Thread(target=connect_client, daemon=True).start()
    
    def _on_client_connected(self, client: Client):
        """Called when client successfully connects (on main thread)."""
        self.client = client
        
        # Set up message callback to handle incoming messages
        # This will be used by ConversationView
        if self.conversationView:
            self.conversationView.set_client(self.client)
        
        print("Client connected successfully!")
    
    def _on_client_connection_error(self, error: str):
        """Called when client connection fails (on main thread)."""
        print(f"Error initializing client: {error}")
        # Show error to user (might want to use CTkMessagebox here)
        # Optionally navigate back to login view
        from CTkMessagebox import CTkMessagebox
        CTkMessagebox(
            self,
            title='Connection Error',
            message=f'Failed to connect to server:\n{error}',
            icon='warning',
            sound=True
        )
    
    def create_conversation_view(self, receiver_user_id: int, receiver_name: str, photo_path: str | None = None, status: str = "online"):
        """Create a conversation view for chatting with a specific user."""
        if self.client is None:
            print("Error: Client not initialized. Please login first.")
            return
        
        self.conversationView = ConversationView(
            master=self,
            client=self.client,
            receiver_user_id=receiver_user_id,
            receiver_name=receiver_name,
            photo_path=photo_path or str(ASSETS_DIR / 'icon/default-avatar.png'),
            status=status
        )
        return self.conversationView
    
    def __return(self, view = None):
        if view is None:
            if self.previous_view:
                if self.current_view:
                    self.show_view(self.previous_view)
        else:
            self.show_view(view)
    
    def power_on(self):
        self.mainloop()

        
if __name__ == "__main__":
    p = Phone()
    p.mainloop()