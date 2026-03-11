from datetime import date, datetime
from typing import Callable

import customtkinter as ctk
from PIL import Image

from local_chat.client import Client
from local_chat.command.data_loader import (
    get_conversations_between_users,
    load_conversation_messages,
)
from local_chat.config import ASSETS_DIR
from local_chat.gui.widgets.nameplate import NamePlate


class ConversationView(ctk.CTkFrame):
    def __init__(self, master, client: Client, receiver_user_id: int, receiver_name: str, photo_path: str, status: str = "offline"):
        super().__init__(master, fg_color='#FDFDFD')
        self.client = client
        self.current_user_id = client.user_id
        self.receiver_user_id = receiver_user_id
        self.receiver_name = receiver_name
        self.header = ctk.CTkFrame(self, fg_color='#FDFDFD')
        self.entry_frame = ctk.CTkFrame(self, fg_color='#FDFDFD')
        back = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/back_arrow.png').resize((60, 60)))
        send = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/send-icon.png'), size=(60, 60))
        self.text_font = ctk.CTkFont(family='SF Pro Text', weight='normal', size=16)
        self.time_font = ctk.CTkFont(family='SF Pro Text', weight='normal', size=12)
        self.date_font = ctk.CTkFont(family='SF Pro Text', weight='bold', size=10)
        self.back_btn = ctk.CTkButton(
            self.header,
            width=60,
            image=back,
            text='',
            corner_radius=0,
            fg_color='#FDFDFD',
            hover_color="#CCCCCC",
            cursor='hand2',
            )
        self.send_btn = ctk.CTkButton(
            self.entry_frame,
            width=10,
            height=60,
            image=send,
            text='',
            corner_radius=0,
            fg_color='#FDFDFD',
            hover_color="#FDFDFD",
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
        self.send_btn.pack(side=ctk.RIGHT, padx=0)
        self.chat_frame.pack(expand=ctk.TRUE, fill=ctk.BOTH, padx=0, pady=0)
        self.chat_frame._parent_canvas.bind('<Button-1>', lambda e: self.chat_frame.focus_set()) # type: ignore

        # Set up message callback to receive incoming messages
        if self.client:
            self.client.set_message_callback(self._on_message_received)
        self.load_conversation_history()

    def set_back_button_callback(self, callback: Callable):
        self.back_btn.configure(command=callback)

    #I don't wanna fix it cuz it's a small project but loading this from db everytime a user click on the nameplate is wild
    # for perfomance lol
    # TODO: add history caching and delete when user logs off maybe ion know but find a way twan
    def load_conversation_history(self) -> None:
        if not self.current_user_id:
            #TODO: do something, i don't know what yet
            return

        conversation = get_conversations_between_users(
            self.current_user_id,
            self.receiver_user_id
        )

        if conversation is None:
            return

        messages = load_conversation_messages(conversation)

        if messages == []:
            return

        timestamps = [msg['timestamp'] for msg in messages]

        def parse_timestamp(utc_timestamp: str,/, return_date: bool = False):
            utc_time = datetime.fromisoformat(utc_timestamp.replace('Z', '+00:00'))
            local_dt = utc_time.astimezone()
            return local_dt.strftime("%H:%M") if not return_date else local_dt.strftime('%Y-%m-%d')

        def to_local_timestamp(utc_timestamp: str) -> str:
            utc_dt = datetime.fromisoformat(utc_timestamp.replace("Z", "+00:00"))
            local_dt = utc_dt.astimezone()
            return local_dt.strftime("%Y-%m-%dT%H:%M:%S")

        def get_unique_dates(timestamps: list[str]) -> list[str]:
            seen_dates = []
            for timestamp in timestamps:
                local_dt = to_local_timestamp(timestamp)
                if local_dt.split('T')[0] not in seen_dates:
                    seen_dates.append(timestamp.split('T')[0])
            return sorted(seen_dates)

        def make_conversation_date(_date: str) -> str:
            d = _date.split('-')
            return date(int(d[0]), int(d[1]), int(d[2])).strftime('%B %d, %Y')

        unique_dates = get_unique_dates(timestamps)
        current_date = unique_dates.pop(0)
        conversation_date = make_conversation_date(current_date)
        first_pass = True

        for message in messages:
            sender_id = message['sender_id']
            content = message['content']
            timestamp = message['timestamp']
            msg_date = parse_timestamp(timestamp, return_date=True)
            if first_pass:
                first_pass = False
            else:
                if msg_date != current_date:
                    current_date = unique_dates.pop(0)
                    conversation_date = make_conversation_date(current_date)
                else:
                    conversation_date = None

            if sender_id == self.current_user_id:
                side = 'right'
            else:
                side = 'left'

            self.add_message(content, side=side, timestamp=parse_timestamp(timestamp), conversation_date=conversation_date)
        self.after(50, self.scroll_to_bottom)

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

    #TODO: add conversation_date if as the user is sending messages if the date isn't the same
    def add_message(self, text: str, side: str ="right", timestamp: str | None = None, conversation_date: str | None = None):
            bubble_color = "#D1E8FF" if side == "right" else "#F3F3F3"
            text_color = "black"

            if conversation_date:
                date_frame = ctk.CTkFrame(self.chat_frame, fg_color="#E0E0E0", corner_radius=12)
                date = ctk.CTkLabel(
                    date_frame,
                    text=conversation_date,
                    justify="center",
                    text_color=text_color,
                    wraplength=250,
                    font=self.date_font,
                )
                date.pack(padx=5, pady=2)
                date_frame.pack(anchor='center', pady=10)

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

            _timestamp = datetime.now().strftime("%H:%M") if timestamp is None else timestamp
            time_label = ctk.CTkLabel(msg, height=0, text=_timestamp, text_color="gray", font=self.time_font)

            if side == "right":
                bubble.pack(anchor="e", pady=5)
                time_label.grid(row=2, column=2, sticky="s")
            else:
                bubble.pack(anchor="w", pady=5)
                time_label.grid(row=2, column=2, sticky="s")

    def scroll_to_bottom(self):
        self.chat_frame._parent_canvas.yview_moveto(1)

    def send_message(self):
        """Send message through the client to the receiver."""
        import threading

        message_text = self.entry.get("1.0", "end-1c").strip()
        if not message_text:
            return

        self.entry.delete("1.0", "end-1c")

        #TODO: add conv date if the date is different than previous when user sends a new message
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
