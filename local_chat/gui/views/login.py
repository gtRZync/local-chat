import customtkinter as ctk
import tkinter  as tk 
from PIL import Image
from local_chat.config import ASSETS_DIR
from typing import Union, Callable, Any
from local_chat.command.auth import connect
from CTkMessagebox import CTkMessagebox

class LoginView(ctk.CTkFrame):
    def __init__(self, master, back_callback: Union[Callable[[], Any], None]):
        super().__init__(master, fg_color='#FDFDFD', corner_radius=0)
        self.text_font = ctk.CTkFont(family='SF Pro Text', size=16)
        self.user_icon = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/Sample_User_Icon.png').resize((20, 20)))
        self.back_icon = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/chevron_backward.png').resize((60, 60)))
        self.header_icon = ctk.CTkImage(Image.open(ASSETS_DIR / 'icon/header.png'), size=(220, 220))
        self.back = ctk.CTkButton(
            self, 
            width=20,
            text='', 
            image=self.back_icon, 
            fg_color='#FDFDFD', 
            hover_color="#DADADA", 
            command=back_callback, 
            compound='left',
            border_width=0
            )
        self.title = ctk.CTkLabel(
            self, 
            text_color='black', 
            text='',
            image=self.header_icon,
            fg_color='#FDFDFD'
            )
        self.number_frame = ctk.CTkFrame(self, fg_color='#FDFDFD', border_color="#A9A9A6", border_width=2)
        self.number_icon_label = ctk.CTkLabel(self.number_frame, image=self.user_icon, text='')
        self.number_entry = ctk.CTkEntry(
            self.number_frame, 
            height= 40,
            corner_radius=8, 
            placeholder_text='Enter your phone number',
            fg_color="#FEFFFD",
            border_color='#A9A9A6',
            border_width=0,
            font=self.text_font
            )
        self.name_frame = ctk.CTkFrame(self, fg_color='#FDFDFD', border_color="#A9A9A6", border_width=2)
        self.name_icon_label = ctk.CTkLabel(self.name_frame, image=self.user_icon, text='')
        self.name_entry = ctk.CTkEntry(
            self.name_frame, 
            height= 40,
            corner_radius=8, 
            placeholder_text='Enter your name',
            fg_color='#FEFFFD',
            border_color="#A9A9A6",
            border_width=0,
            font=self.text_font
            )
        self.status_label = ctk.CTkLabel(
            self,
            text='',
            text_color='#FF3B30',
            font=ctk.CTkFont(family='SF Pro Text', size=14),
            fg_color='#FDFDFD',
            height=20,
            wraplength=260
        )
        self.continue_btn = ctk.CTkButton(
            self,
            height=56, 
            text='Continue', 
            corner_radius=8, 
            text_color='#DBEFFF', 
            fg_color='#0F9CFF',
            font=ctk.CTkFont(family='SF Pro Text', weight='bold', size=16),
            state=ctk.DISABLED,
            command=self.__handle_connect
            )
        self.after_activate_id = None
        self.__login_command = None
        self.__status: dict[str, bool] = {'logged in' : False}
        self.back.pack(anchor='w', padx=5)
        self.title.pack(pady=(50,5))
        
        self.number_frame.pack(fill=ctk.X, padx=20, pady=20)
        self.number_icon_label.pack(side=ctk.LEFT, padx=(10, 0), pady=2)
        self.number_entry.pack(padx=(0, 20), pady=2, fill=ctk.X)
        
        self.name_frame.pack(fill=ctk.X, padx=20, pady=(0, 20))
        self.name_icon_label.pack(side=ctk.LEFT, padx=(10, 0), pady=2)
        self.name_entry.pack(padx=(0, 20), pady=2, fill=ctk.X)
        
        self.status_label.pack(padx=20, pady=(0, 5), fill=ctk.X)
        self.continue_btn.pack(padx=20, pady=10, fill=ctk.X)
        self.name_entry.bind('<Key>', self.__activate_btn)
        self.number_entry.bind('<Key>', self.__activate_btn)
        self.bind('<Button-1>', lambda event: self.__shift_focus(event))
        self.title.bind('<Button-1>', lambda event: self.__shift_focus(event))
        self.name_entry.bind('<Key>', self.__on_enter)
        self.number_entry.bind('<Key>', self.__on_enter)
        self.number_entry.after(1, self.__number_limit)
        
    def __on_enter(self, event: tk.Event):
        if event.keysym.lower() == 'return':
            self.continue_btn.invoke()
        
    def __shift_focus(self, event: tk.Event):
        if (event.widget is self._canvas or
            event.widget is self.title._label): # type: ignore
            self.focus()
    
    def __number_limit(self):
        if len(self.number_entry.get()) > 10:
            self.number_entry.delete(10, ctk.END)
        self.number_entry.after(1, self.__number_limit)
            
    def on_login(self, command: Callable[[], Any]):
        self.__login_command = command
        
    def __handle_connect(self):
        """Handle the connect/authentication process."""
        try:
            
            phone_number = self.number_entry.get().strip()
            if phone_number.startswith('+'):
                phone_number = phone_number.replace('+', '0')
                
            int(phone_number)
            username = self.name_entry.get().strip()
            
            success, message = connect(phone_number, username)
            
            if success:
                self.__status['logged in'] = True
                self.__show_status(message, is_error=False)
                self.after(2000, self.__continue)
            else:
                self.__status['logged in'] = False
                self.__show_status(message, is_error=True)
                
        except ValueError:
            self.__show_status("Please enter a valid phone number", is_error=True)
        except Exception as e:
            self.__show_status(f"An error occurred: {str(e)}", is_error=True)
    
    def __show_status(self, message: str, is_error: bool = True):
        """Display status message in the status label."""
    
        self.status_label.configure(text=message)
        if is_error:
            self.status_label.configure(text_color='#FF3B30')
        else:
            self.status_label.configure(text_color='#34C759')
    
    def __continue(self, event=None):
        if self.__status['logged in']:
            if self.__login_command:
                self.__login_command()
            else:
                CTkMessagebox(
                    self.master, 
                    title='Login Error', 
                    message='Login Command not set\nPlease call LoginView.on_login(...) before retrying',
                    icon='warning',
                    sound=True
                    )
             
    @property            
    def logged_in(self):
        return self.__status['logged in']
    
    @property
    def phone_number(self) -> str:
        """Get the phone number from the entry field."""
        phone = self.number_entry.get().strip()
        if phone.startswith('+'):
            phone = phone.replace('+', '0')
        return phone
    
    @property
    def username(self) -> str:
        """Get the username from the entry field."""
        return self.name_entry.get().strip()
    
    def __activate_btn(self, event):
        if (len(self.name_entry.get().strip()) > 2 and
            len(self.number_entry.get()) == 10):
            self.continue_btn.configure(state=ctk.NORMAL)
            if self.after_activate_id:
                self.after_cancel(self.after_activate_id)
                self.after_activate_id = None
                return
        else:
            self.continue_btn.configure(state=ctk.DISABLED)
        self.after_activate_id = self.after(100, lambda: self.__activate_btn(event))
            