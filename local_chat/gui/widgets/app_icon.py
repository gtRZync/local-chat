import tkinter as tk
from PIL import ImageTk
import customtkinter as ctk
from local_chat.utils import Vector2i

class AppIcon:
    def __init__(
        self, 
        canvas: tk.Canvas, 
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
        self.font = font or ctk.CTkFont(family='Arial', size=16)
        self.__icon_id = canvas.create_image(pos.x, pos.y, image=image, anchor=anchor)
        self.__TEXT_PADY = 20
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
        self._clamp()
        
    
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
            
    def _clamp(self):
        x, y = self.canvas.coords(self.icon_id)
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Grid configuration
        columns = 8  # number of horizontal cells
        rows = 16    # number of vertical cells
        cell_width = canvas_width / columns
        cell_height = canvas_height / rows
    
        # Snap x, y to nearest grid cell
        snapped_x = round(x / cell_width) * cell_width
        snapped_y = round(y / cell_height) * cell_height
    
        # Clamp to canvas boundaries
        snapped_x = min(max(snapped_x, 0), canvas_width - self.icon.width())
        snapped_y = min(max(snapped_y, 0), canvas_height - self.icon.height())
    
        self.canvas.coords(self.icon_id, snapped_x, snapped_y)
    
        self.__text_x = snapped_x + self.icon.width() / 2
        self.__text_y = snapped_y + self.icon.height() + self.__TEXT_PADY
        self.canvas.coords(self.name_id, self.__text_x, self.__text_y)
    
            
                
