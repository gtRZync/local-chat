from datetime import datetime

class TimeUpdatableMixin:
    def update_time(self) -> None:
        text = self.get_time_text()
        curr_time = self.canvas.itemcget(self.time_id, 'text')
        
        if curr_time != text:
            self.canvas.itemconfigure(self.time_id, text=text)
            
        self.canvas.after(200, self.update_time)
        
    @property
    def time_id(self) -> int:
        raise NotImplementedError
    
    def get_time_text(self) -> str:
        return datetime.now().strftime('%H:%M')