import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from local_chat.utils import TimeUpdatableMixin
from local_chat.config import ASSETS_DIR

class StatusBar(TimeUpdatableMixin):
    def __init__(self, canvas: tk.Canvas, canvas_width: int) -> None:
        self.canvas = canvas
        self.font = ctk.CTkFont(family='SF Pro Text', size=18, weight='bold')
        x = self.font.measure(self.get_time_text())
        y = self.font.metrics('linespace')
        self.__time_id = canvas.create_text(
            (canvas.winfo_x() + x/2) + 4,
            canvas.winfo_y() + y/2, 
            text=self.get_time_text(), 
            font=self.font, 
            fill='white'
            )
        con_img = Image.open(ASSETS_DIR / 'icon/connectivity.png')
        self.con_img_tk = ImageTk.PhotoImage(con_img)
        con_x = canvas_width - self.con_img_tk.width() / 2
        self.__conn_id = canvas.create_image(con_x, 10, image=self.con_img_tk)
        cam_img = Image.open(ASSETS_DIR / 'icon/iphone_camera.png').resize((92, 28))
        self.cam_img_tk = ImageTk.PhotoImage(cam_img)
        cam_x = (canvas_width  - (self.cam_img_tk.width() // 2))// 2
        self.__cam_id = canvas.create_image(cam_x, 20, image=self.cam_img_tk)
        self.canvas.after(20, self.update_time)
        
    @property
    def time_id(self) -> int:
        return self.__time_id