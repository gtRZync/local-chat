import tkinter as tk
from PIL import ImageTk
import customtkinter as ctk
from local_chat.utils import Vector2i

class AppIcon:
    def __init__(
        self, 
        canvas: ctk.CTkCanvas, 
        image: ImageTk.PhotoImage, 
        pos: Vector2i, 
        size: Vector2i = Vector2i(-1, -1), #dont know
        app_name: str = 'App Name', 
        anchor = 'nw', 
        font: ctk.CTkFont | None = None 
        ) -> None:
        self.__launch_app = False
        self.__icon_dragged = False
        self.canvas = canvas
        self.icon = image
        self.font = ctk.CTkFont(family='Arial', size=16) if font is None else font
        self.__icon_id = canvas.create_image(pos.x, pos.y, image=image, anchor=anchor)
        self.__TEXT_PADY = 10
        self.__text_x = pos.x + image.width() / 2
        self.__text_y = pos.y + image.height() + self.__TEXT_PADY
        self.__name_id = canvas.create_text(self.__text_x, self.__text_y, font=self.font, text=app_name)
        self.__drag_data = {'x' : 0, 'y' : 0}
        self.canvas.tag_bind(self.__icon_id, '<Button-1>', self.__on_drag_start)
        self.canvas.tag_bind(self.__icon_id, '<ButtonRelease-1>', self.__on_release)
        self.canvas.tag_bind(self.__icon_id, '<B1-Motion>', self.__drag_icon)
        self.canvas.tag_bind(self.__icon_id, '<Enter>', self.__update_cursor)
        self.canvas.tag_bind(self.__icon_id, '<Leave>', self.__update_cursor)
    @property    
    def icon_id(self):
        return self.__icon_id
    @property    
    def name_id(self):
        return self.__name_id
    
    @property
    def width(self) -> int:
        return self.icon.width()
    
    @property
    def height(self) -> int:
        return self.icon.height()
    
    def __on_release(self, event):
        if not self.__icon_dragged:
            self.__launch_app = True
        self.__icon_dragged = False
    
    @property   
    def should_launch_app(self) -> bool:
        return self.__launch_app
    
    def __on_drag_start(self, event: tk.Event):
        self.__drag_data['x'] = event.x
        self.__drag_data['y'] = event.y

    def __drag_icon(self, event: tk.Event):
        if not self.__icon_dragged:
            self.__icon_dragged = True
            self.__launch_app = False
            
        dx = event.x - self.__drag_data['x']        
        dy = event.y - self.__drag_data['y']
        
        self.canvas.move(self.__icon_id, dx, dy)   
        self.canvas.move(self.__name_id, dx, dy)   
        
        self.__drag_data['x'] = event.x
        self.__drag_data['y'] = event.y
    
    def __update_cursor(self, event: tk.Event):
        if event.type == tk.EventType.Enter:
            self.canvas.configure(cursor='hand2')
        elif event.type == tk.EventType.Leave:
            self.canvas.configure(cursor='arrow')
