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
        
        spin_flip_frame = Frame(controls_frame)
        spin_flip_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(spin_flip_frame, "spin_flip", title="Spin or Flip")
        self.set_button(field="spin_flip", label="Spin Left", command=self.spin_left)
        self.set_button(field="spin_flip", label="Spin Right", command=self.spin_right)
        
        if SlTrace.trace("flip_support"):
            self.set_button(field="spin_flip", label="Flip Up/Down", command=self.flip_up_down)
            self.set_button(field="spin_flip", label="Flip Left/Right", command=self.flip_left_right)
        
        add_delete_frame = Frame(controls_frame)
        add_delete_frame.pack(anchor="w", side="left", fill="x", expand=True)

        add_frame = Frame(add_delete_frame)
        add_frame.pack(side="top", fill="x", expand=True)

        add_front_frame = Frame(add_frame)
        add_front_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(add_front_frame, "add", title="Add to Front")
        self.set_button(field="add", label="Straight", command=self.front_add_straight)
        self.set_button(field="add", label="Left Turn", command=self.front_add_left_turn)
        self.set_button(field="add", label="Right Turn", command=self.front_add_right_turn)
        self.set_button(field="add", label="Red Car", command=self.front_add_red_car)
        self.set_button(field="add", label="Blue Car", command=self.front_add_blue_car)
        
        if SlTrace.trace("add_to_back_support"):
            add_back_frame = Frame(add_frame)
            add_back_frame.pack(side="top", fill="x", expand=True)
            self.set_fields(add_back_frame, "add", title="Add to Back")
            self.set_button(field="add", label="Straight", command=self.back_add_straight)
            self.set_button(field="add", label="Left Turn", command=self.back_add_left_turn)
            self.set_button(field="add", label="Right Turn", command=self.back_add_right_turn)

        above_delete_frame = Frame(add_delete_frame)
        above_delete_frame.pack(anchor="w", side="top", fill="both", expand=True)
        self.set_vert_sep(frame=above_delete_frame)
        delete_frame = Frame(add_delete_frame)
        delete_frame.pack(anchor="s", side="top", fill="x", expand=True)

        self.set_fields(delete_frame, "delete", title="Delete")
        self.set_button(field="delete", label="Front", command=self.delete_front)
        self.set_button(field="delete", label="Back", command=self.delete_back)
        self.set_button(field="delete", label="Selected", command=self.delete_selected)
        self.set_button(field="delete", label="All", command=self.delete_all)
        
        select_unselect_frame = Frame(controls_frame)
        select_unselect_frame.pack(anchor="w", side="left", fill="x", expand=True)
        select_frame = Frame(select_unselect_frame)
        select_frame.pack(anchor="w", side="left", fill="x", expand=True)
        self.set_fields(select_frame, "select", title="Select/Unselect:")
        self.set_button(field="select", label="None", command=self.select_none)
        self.set_button(field="select", label="All", command=self.select_all)
        self.set_button(field="select", label="Others", command=self.select_others)
        
        
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

    def select_none(self):
        self.change_control("select_none")       

    def select_all(self):
        self.change_control("select_all")       

    def select_others(self):
        self.change_control("select_others")       
            
    def spin_left(self):
        self.change_control("spin_left")

    
    def spin_right(self):
        self.change_control("spin_right")

    
    def flip_up_down(self):
        self.change_control("flip_up_down")

    
    def flip_left_right(self):
        self.change_control("flip_left_right")

    def front_add_straight(self):
        self.change_control("front_add_straight")

    def front_add_left_turn(self):
        self.change_control("front_add_left_turn")
    
    def front_add_right_turn(self):
        self.change_control("front_add_right_turn")
    
    def front_add_red_car(self):
        self.change_control("front_add_red_car")
    
    def front_add_blue_car(self):
        self.change_control("front_add_blue_car")

    def back_add_straight(self):
        self.change_control("back_add_straight")

    def back_add_left_turn(self):
        self.change_control("back_add_left_turn")
    
    def back_add_right_turn(self):
        self.change_control("back_add_right_turn")
    
    def delete_front(self):
        self.change_control("delete_front")
    
    def delete_back(self):
        self.change_control("delete_back")
    
    def delete_selected(self):
        self.change_control("delete_selected")
    
    def delete_all(self):
        self.change_control("delete_all")
    
    def update_window(self):
        if self.mw is None:
            return

    def clear(self):
        self.set_vals()
        res = self.change_control("clear_track")
        return res

    def set(self):
        self.set_vals()
        res = self.change_control("set_track")
        return res

    
    def reset(self):
        self.set_vals()
        res = self.change_control("reset_track")
        return res

    
    def undo(self):
        self.set_vals()
        res = self.change_control("undo_cmd")
        return res

    
    def redo(self):
        self.set_vals()
        res = self.change_control("redo_cmd")
        return res


    
if __name__ == '__main__':
        
    root = Tk()
    root.withdraw()       # Hide main window

    SlTrace.setProps()
    pW = PositionWindow(title="PositionWindow Testing")
        
    root.mainloop()