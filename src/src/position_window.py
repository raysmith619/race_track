# position_window.py    08_Jul_2019  crs
"""
Window control for part positioning / arrangement
"""
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError
from select_control_window import SelectControlWindow            
        
class PositionWindow(SelectControlWindow):
    CONTROL_NAME_PREFIX = "position_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 0
            
    def _init(self, *args, title=None, control_prefix=None,
              change_control_proc=None,
               **kwargs):
        """ Initialize subclassed SelectControlWindow singleton
             Setup score /undo/redo window
             :change_control_proc: proc called with change indicator
        """
        if title is None:
            title = "Position Parts"
        if control_prefix is None:
            control_prefix = self.CONTROL_NAME_PREFIX
        super()._init(*args, title=title, control_prefix=control_prefix,
                       **kwargs)
        self.change_control_proc = change_control_proc
        if self.display:
            self.control_display()    
            

    def control_display(self):            
        """ display /redisplay controls to enable
        entry / modification
        """
        if self._is_displayed:
            return

        super().control_display()       # Do base work        
        
        controls_frame = self.top_frame
        controls_frame.pack(side="top", fill="x", expand=True)
        
        spin_flip_frame = Frame(controls_frame)
        spin_flip_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(spin_flip_frame, "spin_flip", title="Spin or Flip")
        self.set_button(field="spin_flip", label="Spin Left", command=self.spin_left)
        self.set_button(field="spin_flip", label="Spin Right", command=self.spin_right)
        
        self.set_button(field="spin_flip", label="Flip Up/Down", command=self.flip_up_down)
        self.set_button(field="spin_flip", label="Flip Left/Right", command=self.flip_left_right)
        
        add_delete_frame = Frame(controls_frame)
        add_delete_frame.pack(anchor="w", side="left", fill="x", expand=True)

        add_frame = Frame(add_delete_frame)
        add_frame.pack(side="top", fill="x", expand=True)

        add_front_frame = Frame(add_frame)
        add_front_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(add_front_frame, "add", title="Add to Front")
        self.set_button(field="add", label="Strait", command=self.front_add_strait)
        self.set_button(field="add", label="Left Turn", command=self.front_add_left_turn)
        self.set_button(field="add", label="Right Turn", command=self.front_add_right_turn)
        

        add_back_frame = Frame(add_frame)
        add_back_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(add_back_frame, "add", title="Add to Back")
        self.set_button(field="add", label="Strait", command=self.back_add_strait)
        self.set_button(field="add", label="Left Turn", command=self.back_add_left_turn)
        self.set_button(field="add", label="Right Turn", command=self.back_add_right_turn)

        delete_frame = Frame(add_delete_frame)
        delete_frame.pack(anchor="w", side="top", fill="x", expand=True)
        self.set_fields(delete_frame, "delete", title="Delete")
        self.set_button(field="delete", label="Front", command=self.delete_front)
        self.set_button(field="delete", label="Back", command=self.delete_back)
        
        
        self.arrange_windows()

    """
    Commands
    """
    def change_control(self, change):
        """ Change announce and operation
        :change: change identifier
        """
        SlTrace.lg("change_control:%s" % change)
        if self.change_control_proc is not None:
            self.change_control_proc(change)
            
            
    def spin_left(self):
        self.change_control("spin_left")

    
    def spin_right(self):
        self.change_control("spin_right")

    
    def flip_up_down(self):
        self.change_control("flip_up_down")

    
    def flip_left_right(self):
        self.change_control("flip_left_right")

    def front_add_strait(self):
        self.change_control("front_add_strait")

    def front_add_left_turn(self):
        self.change_control("front_add_left_turn")
    
    def front_add_right_turn(self):
        self.change_control("front_add_right_turn")

    def back_add_strait(self):
        self.change_control("back_add_strait")

    def back_add_left_turn(self):
        self.change_control("back_add_left_turn")
    
    def back_add_right_turn(self):
        self.change_control("back_add_right_turn")
    
    def delete_front(self):
        self.change_control("delete_front")
    
    def delete_back(self):
        self.change_control("delete_back")
    
    def update_window(self):
        if self.mw is None:
            return

        
        
    def undo_button(self):
        self.change_control("undoButton")
        res = self.play_control.undo()
        return res
                
        
    def redo_button(self):
        self.change_control("redoButton")
        res = self.play_control.redo()
        return res


    
if __name__ == '__main__':
        
    root = Tk()
    root.withdraw()       # Hide main window

    SlTrace.setProps()
    pW = PositionWindow(title="PositionWindow Testing")
        
    root.mainloop()