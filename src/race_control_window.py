# race_control_window.py    08_Jul_2019  crs
"""
Window control for race running control
"""
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError
from select_control_window import SelectControlWindow            
        
class RaceControlWindow(SelectControlWindow):
    CONTROL_NAME_PREFIX = "race_control"
    DEF_WIN_X = 500
    DEF_WIN_Y = 0
            
    def _init(self, *args, title=None, control_prefix=None,
              command_control_proc=None,
               **kwargs):
        """ Initialize subclassed SelectControlWindow singleton
             Setup score /undo/redo window
             :command_control_proc: proc called with change indicator
        """
        if title is None:
            title = "Racing Control"
        if control_prefix is None:
            control_prefix = self.CONTROL_NAME_PREFIX
        super()._init(*args, title=title, control_prefix=control_prefix,
                       **kwargs)
        self.command_control_proc = command_control_proc
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
        
        setup_frame = Frame(controls_frame)
        setup_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(setup_frame, "spin_flip", title="Race Running")
        self.set_button(field="race", label="Setup", command=self.race_setup)
        self.set_button(field="race", label="Start", command=self.race_start)
        self.set_button(field="race", label="Pause", command=self.race_pause)
        self.set_button(field="race", label="Continue", command=self.race_continue)
        self.set_button(field="race", label="Stop", command=self.race_stop)

        running_frame = Frame(setup_frame)
        running_frame.pack(side="top", fill="x", expand=True)
        self.set_fields(running_frame, "run", title="Running")
        self.set_button(field="running", label="Faster", command=self.race_faster)
        self.set_button(field="running", label="Slower", command=self.race_slower)
         
        
        self.arrange_windows()

    """
    Commands
    """
    def command_control(self, command):
        """ Change announce and operation
        :change: change identifier
        """
        SlTrace.lg("command_control:%s" % command)
        if self.command_control_proc is not None:
            self.command_control_proc(command)
            
    def race_setup(self):
        self.command_control("race_setup")
            
    def race_start(self):
        self.command_control("race_start")
            
    def race_continue(self):
        self.command_control("race_continue")
            
    def race_pause(self):
        self.command_control("race_pause")
            
    def race_stop(self):
        self.command_control("race_stop")

            
    def race_faster(self):
        self.command_control("race_faster")
            
    def race_slower(self):
        self.command_control("race_slower")
 
    
    def update_window(self):
        if self.mw is None:
            return

    def set(self):
        self.set_vals()
        res = self.command_control("set_track")
        return res

    
    def reset(self):
        self.set_vals()
        res = self.command_control("race_reset")
        return res

    
    def undo(self):
        self.set_vals()
        res = self.command_control("race_undo")
        return res

    
    def redo(self):
        self.set_vals()
        res = self.command_control("race_redo")
        return res


    
if __name__ == '__main__':
        
    root = Tk()
    root.withdraw()       # Hide main window

    SlTrace.setProps()
    pW = RaceControlWindow(title="RaceControlWindow Testing")
        
    root.mainloop()