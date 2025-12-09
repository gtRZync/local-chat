import customtkinter as ctk
from PIL import Image
from local_chat.config import ASSETS_DIR
from typing import Callable, Any
from local_chat.gui.widgets.nameplate import NamePlate

class ChatListView(ctk.CTkFrame):
    def __init__(self, master, back_command: Callable[[], Any], contact_list: list[tuple] | None = None):
        super().__init__(master, fg_color='#FDFDFD', corner_radius=0)
        self.contacts = [
            ( ASSETS_DIR / 'icon/default-avatar.png' , 'Jhon Doe' , 'Online', ),
            ( ASSETS_DIR / 'icon/default-avatar.png' , 'Michael Brown', 'Offline'), 
            ( ASSETS_DIR / 'icon/default-avatar.png' , 'Emily Johnson', 'Online') 
            ]
        
        self.header_font = ctk.CTkFont(family='SF Pro Display', weight='bold', size=35)
        self.text_font = ctk.CTkFont(family='SF Pro Text', weight='normal', size=16)
        self.back_icon = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/chevron_backward.png').resize((60, 60)))
        self.header_text = 'Chat'
        self.back = ctk.CTkButton(
            self, 
            width=20,
            text='', 
            image=self.back_icon, 
            fg_color='#FDFDFD', 
            hover_color="#DADADA", 
            command=back_command, 
            compound='left',
            border_width=0
            )
        self.title = ctk.CTkLabel(
            self, 
            text_color='black', 
            text=self.header_text, 
            font=self.header_font, 
            fg_color='#FDFDFD'
            )
        
        self.search_icon = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/search-icon.png').resize((20, 20)))
        self.search_frame = ctk.CTkFrame(self, fg_color='#EDEDED', border_width=0)
        self.search_icon_label = ctk.CTkLabel(self.search_frame, image=self.search_icon, text='')
        self.search_entry = ctk.CTkEntry(
            self.search_frame, 
            height= 30,
            corner_radius=8, 
            placeholder_text='Search',
            placeholder_text_color= 'black',
            fg_color="#EDEDED",
            border_width=0,
            font=self.text_font
            )
        self.chat_list = ctk.CTkScrollableFrame(
            self, 
            scrollbar_fg_color='#FDFDFD', 
            fg_color='#FDFDFD', 
            scrollbar_button_color='#FDFDFD'
            )
        self.no_contact = ctk.CTkLabel(
            self.chat_list, 
            fg_color='#FDFDFD',
            text='No Contact',
            font=self.text_font,
            anchor='center'
            )
        self.back.pack(anchor='w', padx=5)
        self.title.pack(pady=(20,5), padx=20, anchor='nw')
        
        self.search_frame.pack(fill=ctk.X, padx=20, pady=(0, 30))
        self.search_icon_label.pack(side=ctk.LEFT, padx=(10, 0), pady=2)
        self.search_entry.pack(padx=(0, 20), pady=2, fill=ctk.X)
        self.chat_list.pack(expand=True, fill=ctk.BOTH)
        self.load_contacts()
    
    def load_contacts(self):
        if self.contacts:
            for img_path, username, status in self.contacts:
                NamePlate(self.chat_list, img_path, username, status).pack(pady=5, fill=ctk.X)
        else:
            self.no_contact.pack(expand=True, fill=ctk.BOTH, pady=(200, 0))
