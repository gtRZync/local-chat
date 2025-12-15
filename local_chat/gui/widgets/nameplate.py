from typing import Callable
import customtkinter as ctk
from PIL import Image

class NamePlate(ctk.CTkFrame):
    def __init__(self, master, photo_path, name: str, status: str, on_click : Callable | None =None, hover= True, **kwargs):
        cursor = 'hand2' if hover else 'arrow'
        super().__init__(master, fg_color='#FDFDFD', border_width=0, cursor=cursor, **kwargs)
        self.text_font = ctk.CTkFont(family='SF Pro Text', weight='normal', size=16)
        self.text_font_bold = ctk.CTkFont(family='SF Pro Text', weight='bold', size=18)
        self.on_click = on_click #TODO: make the photo clickable
        self.hover = hover
        self.avatar = ctk.CTkImage(Image.open(photo_path), size=(70, 70)) 
        self.pfp_label = ctk.CTkLabel(self, text='', image=self.avatar)

        self.name_stat_frame = ctk.CTkFrame(self, fg_color='#FDFDFD', border_width=0)
        
        self.username = name
        self.uname = ctk.CTkLabel(self.name_stat_frame, text=name, text_color='black', font=self.text_font_bold)

        self.status_frame = ctk.CTkFrame(self.name_stat_frame, fg_color='#FDFDFD', border_width=0)
        self.status_indic = ctk.CTkLabel(self.status_frame, text='●', text_color=self.get_status_color(status), fg_color='#FDFDFD', font=self.text_font)
        self.status_indic_text = ctk.CTkLabel(self.status_frame, text=status, text_color='black', fg_color='#FDFDFD', font=self.text_font)

        self.pack(fill=ctk.X, pady=10)
        self.pfp_label.pack(side=ctk.LEFT, padx=10)
        self.name_stat_frame.pack(side=ctk.LEFT)
        self.uname.pack(padx=4)
        self.status_frame.pack(anchor='w')
        self.status_indic.pack(side=ctk.LEFT, padx=(0, 5))
        self.status_indic_text.pack(side=ctk.LEFT)
        
        if self.hover:
            self.bind_events()
    
    def get_status_color(self, status: str) -> str:
        if status.lower().strip() == 'online':
            return '#7AAD67'
        return "#ADB3B4"
        
    def update_status(self, new_status: str):
        self.status_indic.configure(text_color=self.get_status_color(new_status))
        self.status_indic_text.configure(text=new_status)
    
    #brace urself lol very profesionnal code incomming 😭
    def bind_events(self):
        self.__bind_event(self)
        self.__bind_event(self.uname)
        self.__bind_event(self.pfp_label)
        self.__bind_event(self.status_frame)
        self.__bind_event(self.status_indic)
        self.__bind_event(self.name_stat_frame)
        self.__bind_event(self.status_indic_text)
    
    def __bind_event(self, widget: ctk.CTkBaseClass):
        widget.bind('<Button-1>', self.handle_click)
        widget.bind('<Enter>', lambda e: self.configure(fg_color="#DADADA"))
        widget.bind('<Leave>', lambda e: self.configure(fg_color='#FDFDFD'))
        widget.bind('<Enter>', lambda e: self.name_stat_frame.configure(fg_color="#DADADA"), add='+')
        widget.bind('<Leave>', lambda e: self.name_stat_frame.configure(fg_color='#FDFDFD'), add='+')
        widget.bind('<Enter>', lambda e: self.status_frame.configure(fg_color="#DADADA"), add='+')
        widget.bind('<Leave>', lambda e: self.status_frame.configure(fg_color='#FDFDFD'), add='+')
        widget.bind('<Enter>', lambda e: self.status_indic.configure(fg_color="#DADADA"), add='+')
        widget.bind('<Leave>', lambda e: self.status_indic.configure(fg_color='#FDFDFD'), add='+')
        widget.bind('<Enter>', lambda e: self.status_indic_text.configure(fg_color="#DADADA"), add='+')
        widget.bind('<Leave>', lambda e: self.status_indic_text.configure(fg_color='#FDFDFD'), add='+')
        
    def handle_click(self, event):
        self.focus_set()
        if self.on_click:
            self.on_click()