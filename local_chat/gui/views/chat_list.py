import customtkinter as ctk
from PIL import Image
from local_chat.client.client import Client
from local_chat.command.data_loader import get_contacts_for_user
from local_chat.config import ASSETS_DIR
from typing import Callable, Any
from local_chat.gui.widgets.nameplate import NamePlate

class ChatListView(ctk.CTkFrame):
    def __init__(self, master, client: Client | None, back_command: Callable[[], Any], current_user_id: int | None = None):
        super().__init__(master, fg_color='#FDFDFD', corner_radius=0)
        self.client = client
        self.default_avatar = ASSETS_DIR / 'icon/default-avatar.png' #TODO: decide wheter to put it in config
        self.current_user_id = current_user_id
        self.contacts: list[dict] = []
        self.nameplates: dict[int, NamePlate] = {}
        
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
        self._load_contacts()
        
    def set_client(self, client: Client):
        self.client = client
    
    def _load_contacts(self) -> None:
        """
        Load contacts from conversations database
        """
        if self.current_user_id is None:
            self.show_no_contacts()
            return 
            
        contact_data = get_contacts_for_user(self.current_user_id)
        if contact_data == []:
            self.show_no_contacts()
            return
            
        for contact in contact_data:
            if contact['user_id'] not in self.nameplates:
                contact_dict = {
                    'photo_path' :      contact['photo_path'],
                    'name' :            contact['name'],
                    'status' :          contact['status'],
                    'user_id' :         contact['user_id'],
                    'conversation_id' : contact['conversation_id']
                }
                self.contacts.append(contact_dict)
            
        self.display_contacts()
        
    def create_contact(self, photo_path: str, name: str, status: str, user_id: int, convo_id: int):
        return tuple([photo_path, name, status, user_id, convo_id])
        
    def display_contacts(self) -> None:
        self.no_contact.pack_forget()
        for contact in self.contacts:
            if contact['user_id'] not in self.nameplates:
                img_path, username, status, user_id, conv_id = contact.values()
                nameplate = NamePlate(
                    self.chat_list,
                    img_path or self.default_avatar,
                    username,
                    status,
                    on_click= lambda uid=user_id, name=username, stat = status:
                        self.open_conversation(uid, name, stat)
                )
                nameplate.pack(pady=5, fill=ctk.X)
                self.nameplates[user_id] = nameplate
            
    
    def open_conversation(self, receiver_uid: int ,receiver_name: str, status: str):
        master = self.master
        
        conversation_view = master.create_conversation_view( 
            receiver_user_id=receiver_uid,
            receiver_name=receiver_name,
            status=status
        )
        master.show_view(conversation_view)
            
    def show_no_contacts(self):
        self.no_contact.pack(expand=True, fill=ctk.BOTH, pady=(200, 0))
