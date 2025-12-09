import customtkinter as ctk
from local_chat.gui.widgets.nameplate import NamePlate
from local_chat.client import Client
from local_chat.config import ASSETS_DIR
from PIL import Image
from datetime import datetime
from typing import Optional

class ConversationView(ctk.CTkFrame):
    def __init__(self, master, client: Client, receiver_user_id: int, receiver_name: str, photo_path: str, status: str = "online"):
        super().__init__(master, fg_color='#FDFDFD')
        self.client = client
        self.receiver_user_id = receiver_user_id
        self.receiver_name = receiver_name
        self.header = ctk.CTkFrame(self, fg_color='#FDFDFD')
        self.entry_frame = ctk.CTkFrame(self, fg_color='#FDFDFD')
        back = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/back_arrow.png').resize((60, 60)))
        send = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/send-icon.png').resize((100, 100)))  
        self.text_font = ctk.CTkFont(family='SF Pro Text', weight='normal', size=16)
        self.time_font = ctk.CTkFont(family='SF Pro Text', weight='normal', size=12)
        self.back_btn = ctk.CTkButton(
            self.header, 
            width=60, 
            image=back,
            text='', 
            corner_radius=0, 
            fg_color='#FDFDFD', 
            hover_color="#CCCCCC",
            cursor='hand2'
            )
        #TODO: fix size
        self.send_btn = ctk.CTkButton(
            self.entry_frame, 
            width=60, 
            height=60, 
            image=send,
            text='',
            corner_radius=60, 
            fg_color='#FDFDFD', 
            hover_color="#CCCCCC",
            cursor='hand2',
            command=self.send_message
            )
        self.nameplate = NamePlate(self.header, photo_path, receiver_name, status, corner_radius=0, hover=False)
        self.header.pack(fill=ctk.X)
        self.line = ctk.CTkFrame(self, height=2, fg_color="#DDDDDD", corner_radius=0)
        self.entry = ctk.CTkTextbox(
            self.entry_frame, 
            fg_color='#FFFFFF',
            text_color='black',
            height=45, 
            corner_radius=12,
            border_color="#DDDDDD",
            border_width=2
            )
        self.chat_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color='#FDFDFD', 
            scrollbar_button_color='#FDFDFD', 
            scrollbar_button_hover_color='#FDFDFD',
            scrollbar_fg_color='#FDFDFD'
            )
        
        self.back_btn.pack(side=ctk.LEFT, padx=0, fill=ctk.BOTH)
        self.nameplate.pack(side=ctk.RIGHT,expand=True, padx=0, pady=0, fill=ctk.BOTH)
        self.line.pack(fill=ctk.X, padx=0, pady=0, anchor=ctk.N)
        self.entry_frame.pack(anchor=ctk.S, side=ctk.BOTTOM, pady=(0, 30), padx=10, fill=ctk.X)
        self.entry.pack(fill=ctk.X, expand=True, side=ctk.LEFT, padx=0)
        self.send_btn.pack(fill=ctk.X, side=ctk.RIGHT, padx=0)
        self.chat_frame.pack(expand=ctk.TRUE, fill=ctk.BOTH, padx=0, pady=0)
        self.chat_frame._parent_canvas.bind('<Button-1>', lambda e: self.chat_frame.focus_set()) # type: ignore
        
        # Set up message callback to receive incoming messages
        if self.client:
            self.client.set_message_callback(self._on_message_received)
    
    def set_client(self, client: Client):
        """Update the client instance and set message callback."""
        self.client = client
        if self.client:
            self.client.set_message_callback(self._on_message_received)
    
    def _on_message_received(self, sender_id: int, sender_name: str, message_content: str):
        """Handle incoming messages from the server.
        This is called from a background thread, so we need to schedule UI updates on main thread.
        
        We don't want no race condition hey 😎
        """
        # Only display messages from the current conversation partner
        if sender_id == self.receiver_user_id:
            # Schedule UI update on main thread using after()
            self.after(0, lambda: self.add_message(message_content, side="left"))
    
    def add_message(self, text, side="right"):
            bubble_color = "#D1E8FF" if side == "right" else "#F3F3F3"
            text_color = "black"

            bubble = ctk.CTkFrame(self.chat_frame, fg_color=bubble_color, corner_radius=12)
            msg = ctk.CTkLabel(
                bubble,
                text=text,
                justify="left",
                text_color=text_color,
                wraplength=250,
                font=self.text_font
            )
            msg.pack(padx=10, pady=6)

            timestamp = datetime.now().strftime("%H:%M")
            time_label = ctk.CTkLabel(self.chat_frame, text=timestamp, text_color="gray", font=self.time_font)

            if side == "right":
                bubble.pack(anchor="e", pady=5)
                time_label.pack(anchor="e")
            else:
                bubble.pack(anchor="w", pady=5)
                time_label.pack(anchor="w")
                
    def send_message(self):
        """Send message through the client to the receiver."""
        import threading
        
        message_text = self.entry.get("1.0", "end-1c").strip()
        if not message_text:
            return
        
        # Clear input immediately for better UX
        self.entry.delete("1.0", "end-1c")
        
        # Display message optimistically (right side for sent messages)
        self.add_message(message_text, side="right")
        
        # Send message via client in background thread to avoid blocking UI
        if self.client and self.client.user_id:
            def send_in_background():
                try:
                    success = self.client.send_message(self.receiver_user_id, message_text)
                    if not success:
                        # Show error on main thread if send failed
                        self.after(0, lambda: self._show_send_error(message_text))
                except Exception as e:
                    # Show error on main thread
                    self.after(0, lambda: self._show_send_error(message_text, str(e)))
            
            threading.Thread(target=send_in_background, daemon=True).start()
        else:
            print("Error: Client not available or not authenticated")
            self._show_send_error(message_text, "Client not connected")
    
    def _show_send_error(self, message_text: str, error: str | None= None):
        """Show error message when send fails."""
        # TODO: Show error message to user (maybe remove the message bubble or show error)
        print(f"Failed to send message to user {self.receiver_user_id}: {error or 'Unknown error'}")
        # Optionally, I could remove the message bubble or show a retry option, i'm tired of coding bruv