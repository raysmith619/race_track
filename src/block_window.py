# block_window.py 19Sep2018
"""
Program Level Menu control
 From BlockWindow(select_window)
"""
import os
import sys
import time

import tkinter as tk
import textwrap

from select_trace import SlTrace
from trace_control_window import TraceControlWindow
from psutil._psutil_windows import proc_cmdline
from scrolled_text_info import ScrolledTextInfo

# Here, we are creating our class, Window, and inheriting from the Frame
# class. Frame is a class from the tkinter module. (see Lib/tkinter/__init__)
class BlockWindow(tk.Frame):
    CONTROL_NAME_PREFIX = "play_control"
    def __deepcopy__(self, memo=None):
        """ provide deep copy by just passing shallow copy of self,
        avoiding tkparts inside sel_area
        """
        SlTrace.lg("SelectArea __deepcopy__", "copy")
        return self
            
        
    # Define settings upon initialization. Here you can specify
    ###@profile    
    def __init__(self,
                 master=None,
                 title=None,
                 control_prefix=None,
                 pgmExit=None,
                 cmd_proc=False,
                 cmd_file=None,
                 arrange_selection=True,
                 game_control=None,
                 games=[],          # text, proc pairs
                 actions=[],
                 changing_pause_time=.1,    # pause (sec) to indicate change is done
                 changing_size_proc=None,

                 ):
        """ Setup window controls
        :arrange_selection: - incude arrangement controls
                        default: True
        :size_chg_pause_time: pause (msec) to indicate change is done
        :changing_size_proc: called when track changes size
                with: changing_size_proc(self)
                        infos: self.changing_width, self.changing_height
        """
        # parameters that you want to send through the Frame class. 
        tk.Frame.__init__(self, master)   

        #reference to the master widget, which is the tk window                 
        self.title = title
        self.master = master
        if control_prefix is None:
            control_prefix = BlockWindow.CONTROL_NAME_PREFIX
        self.control_prefix = control_prefix
        self.arrange_selection = arrange_selection
        self.pgmExit = pgmExit
        self.game_control = game_control
        master.protocol("WM_DELETE_WINDOW", self.pgm_exit)
        self.games = games
        self.actions = actions
        self.tc = None          # Trace control
        self.arc = None         # Arrangement control
        self.arc_call_d = {}     # arc call back functions
        self.cmd_proc = cmd_proc    # Setup command file processing
        self.cmd_file = cmd_file    # if not None, execute this cmd file
        #with that, we want to then run init_window, which doesn't yet exist
        self.init_window()
        self.file_save_proc = None
        self.file_load_proc = None
        
        self.prev_width = None
        self.prev_height = None
        self.changing_pause_time = changing_pause_time
        self.changing_size = False           # Look till resizing has stopped
        self.changing_time = None           # Time of most recent size
        self.changing_width = None          # new changed size
        self.changing_height = None
        self.changing_call_id = None
        self.changing_size_proc = changing_size_proc
        
    def set_file_save_proc(self, proc):
        """ Save File Menu save cmd
        :proc: Save file cmd
        """
        self.file_save_proc = proc

    
    def set_file_load_proc(self, proc):
        """ Save File Menu save cmd
        :proc: Save file cmd
        """
        self.file_load_proc = proc
        
        
    #Creation of init_window
    def init_window(self):

        # changing the title of our master widget 
        if self.title is not None:
            self.master.title(self.title)

        # allowing the widget to take the full space of the root window
        self.pack(fill=tk.BOTH, expand=tk.YES)

        # creating a menu instance
        menubar = tk.Menu(self.master)
        self.menubar = menubar      # Save for future reference
        self.master.config(menu=menubar)

        # create the file object)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load", command=self.File_Load)
        filemenu.add_command(label="Save", command=self.File_Save)
        filemenu.add_separator()
        filemenu.add_command(label="Log", command=self.LogFile)
        filemenu.add_command(label="Properties", command=self.Properties)
        filemenu.add_separator()
        ###filemenu.add_comand(label="Cmd", command=self.command_proc)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.pgmExit)
        menubar.add_cascade(label="File", menu=filemenu)
        
                                # Trace control
        menubar.add_cascade(label=" "*5)
        menubar.add_command(label="Trace", command=self.trace_control)
        self.arrange_windows()
        self.master.bind( '<Configure>', self.win_size_event)

        # create Help object
        menubar.add_cascade(label=" "*50)
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="General", command=self.Help_General)
        helpmenu.add_command(label="Keys", command=self.Help_Keys)
        menubar.add_cascade(label="Help", menu=helpmenu)



    def get_game_control(self):
        """ Retrieve game control to pass to SelectPlay
        """
        return self.game_control
    

    def win_size_event(self, event):
        """ Window sizing event
        """
        win_x = self.master.winfo_x()
        win_y = self.master.winfo_y()
        win_width = self.master.winfo_width()
        win_height = self.master.winfo_height()
        self.set_prop_val("win_x", win_x)
        self.set_prop_val("win_y", win_y)
        self.set_prop_val("win_width", win_width)
        self.set_prop_val("win_height", win_height)
        now = time.time()
        if self.changing_size:
            #SlTrace.lg(f"{win_width = } {self.changing_width = } {win_height = } {self.changing_height = } ")
            if win_width != self.changing_width and win_height != self.changing_height:
                self.changing_width = win_width
                self.changing_height = win_height                
                self.changing_scale_after_pause()
            else:
                pass                # waiting for pause call back
        elif self.prev_width is not None and self.prev_height is not None:
            if win_width != self.prev_width or win_height != self.prev_height:
                self.changing_size = True           # Look till resizing has stopped
                self.changing_width = win_width
                self.changing_height = win_height
                self.changing_scale_after_pause()

        self.prev_width = win_width
        self.prev_height = win_height
        SlTrace.lg(f"win_size_event: {win_width = } {win_height = }", "win_size_event")

    def changing_scale_after_pause(self, pause_time=None, call_id=None):
        """Set / reset changinging pause time out
        :pause: call after pause in change (sec)
        :call_id:  id returned from after
            default: setup
        """
        if pause_time is None:
            pause_time = self.changing_pause_time
            
        time_pause_msec = int(pause_time*1000)
        if call_id is None:
            call_id = self.changing_call_id
        if call_id is not None:            
            self.master.after_cancel(call_id)     # Cancel one in progress
        self.changing_call_id = self.master.after(time_pause_msec, self.changing_track_scale)
               
    def changing_track_scale(self):
        """ Scall drawing to window size change
        """
        self.changing_call_id = None
        SlTrace.lg(f"changing_scale: { self.changing_width = } {self.changing_height}")
        if self.changing_size_proc is not None:
            self.changing_size_proc(self)                    
    
    def arrange_windows(self):
        """ Arrange windows
            Get location and size for properties if any
        """
        win_x = self.get_prop_val("win_x", 50)
        if win_x < 0 or win_x > 1400:
            win_x = 50
        win_y = self.get_prop_val("win_y", 50)
        if win_y < 0 or win_y > 1400:
            win_y = 50
        
        win_width = self.get_prop_val("win_width", self.master.winfo_width())
        win_height = self.get_prop_val("win_height", self.master.winfo_height())
        geo_str = "%dx%d+%d+%d" % (win_width, win_height, win_x, win_y)
        self.master.geometry(geo_str)
        
    
    def get_prop_key(self, name):
        """ Translate full  control name into full Properties file key
        """        
        key = self.control_prefix + "." + name
        return key

    def get_prop_val(self, name, default):
        """ Get property value as (string)
        :name: field name
        :default: default value, if not found
        :returns: "" if not found
        """
        prop_key = self.get_prop_key(name)
        prop_val = SlTrace.getProperty(prop_key)
        if prop_val is None:
            return default
        
        if isinstance(default, int):
            if prop_val == "":
                return 0
           
            return int(prop_val)
        elif isinstance(default, float):
            if prop_val == "":
                return 0.
           
            return float(prop_val)
        else:
            return prop_val

    def set_prop_val(self, name, value):
        """ Set property value as (string)
        :name: field name
        :value: default value, if not found
        """
        prop_key = self.get_prop_key(name)
        SlTrace.setProperty(prop_key, str(value))
        
        
    def pgm_exit(self):
        if self.pgmExit is not None:
            self.pgmExit()
        else:
            sys.exit()    
            
    def File_Load(self):
        if self.file_load_proc is not None:
            return self.file_load_proc()
        
        print("File_Load to be determined")

    def File_Save(self):
        if self.file_save_proc is not None:
            return self.file_save_proc()
        
        print("File_Save to be determined")

    def add_menu_command(self, label=None, call_back=None):
        """ Add simple menu command to top menu
        :label: command label
        :call_back: function to be called when selected
        """
        self.menubar.add_command(label=label, command=call_back)


    def command_proc(self):
        """ Setup command processing options / action
        """
        
        
    def get_arc(self):
        """ Return reference to arrange control
        """
        return self.arc
    
    
    def LogFile(self):
        print("Display Log File")
        abs_logName = SlTrace.getLogPath()
        SlTrace.lg("Log file  %s"
                    % abs_logName)
        ###osCommandString = "notepad.exe %s" % abs_propName
        ###os.system(osCommandString)
        import subprocess as sp
        programName = "notepad.exe"
        sp.Popen([programName, abs_logName])
    
    
    def Properties(self):
        print("Display Properties File")
        abs_propName = SlTrace.defaultProps.get_path()
        SlTrace.lg("properties file  %s"
                    % abs_propName)
        ###osCommandString = "notepad.exe %s" % abs_propName
        ###os.system(osCommandString)
        import subprocess as sp
        programName = "notepad.exe"
        sp.Popen([programName, abs_propName])
        
        
    def select_all(self):
        if self.tc is None:
            self.select_trace()
        self.tc.select_all()
        
            
    def select_none(self):
        if self.tc is None:
            self.select_trace()
        self.tc.select_none()

    def Help_General(self):
        """ General help on games
        """
        title = "General Help"
        help_text = """
        This program facilitates the creation of simple
        two-dimentional race tracks, each supporting
        the racing of a number of two-dimentional cars.
        
        The racing is very simple.  The fun, so far, is
        the creation of various closed path tracks and
        the placement of an arbitrary number of cars on
        each.
        
        The mouse can select a road track from the bin
        below.  Then click the desired position on the
        green track area.
        
        The Position Parts window supports modifying
        the the road part on the track.
        """
        # Place help window to right, bottom of our window
        w_x = self.master.winfo_x()
        w_y = self.master.winfo_y()
        w_h = self.master.winfo_height()
        w_w = self.master.winfo_width()
        wt_x = w_x + w_w
        wt_y = w_y + w_h
        htext = textwrap.dedent(help_text)
        sti = ScrolledTextInfo(title= title,
                      text=htext,
                      xpos=wt_x, ypos=wt_y)

    def Help_Keys(self):
        """ Help on keyboard contorls
        """
        title = "Help on keyboard controls"
        help_text = """
        Add next block, extending track if possible,
        else removing last block added:
            Up, Right, Down, Left - extend track in
            that direction, if current direction,
            or new direction.  If direction key
            is backwards, towards the current track,
            remove the current track block.  This
            shortens the track.
            Key presses can be repeated to aid
            creating the track.

        """
        htext = textwrap.dedent(help_text)
        # Place help window to right, bottom of our window
        x_disp = 100
        y_disp = 100
        w_x = self.master.winfo_x()
        w_y = self.master.winfo_y()
        w_h = self.master.winfo_height()
        w_w = self.master.winfo_width()
        wt_x = w_x + w_w + x_disp
        wt_y = w_y + w_h + y_disp
        htext = textwrap.dedent(help_text)
        sti = ScrolledTextInfo(title= title,
                      text=htext,
                      xpos=wt_x, ypos=wt_y)
         

    def arrange_control(self):
        """ Create arrangement window
        :returns: ref to ArrangeControl object
        """
        if self.arc is not None:
            self.arc.delete_window()
            self.arc = None
        
        '''Not using ArrangeControl for now
        self.arc = ArrangeControl(self, title="Arrange")
        for callname, callfn in self.arc_call_d.items():     # Enable any call back functions
            self.arc.set_call(callname, callfn)
        return self.arc
        '''
    def ctl_list(self, ctl_name, selection_list):
        return self.arc.ctl_list(ctl_name, selection_list)


    def get_ctl_entry(self, name):
        """ Get control value.  If none return default
        """
        if self.arc is None:
            return None
        return self.arc.get_entry_val(name)
 

    def get_current_val(self, name, default=None):
        """ Get control value.  If none return default
        """
        if self.arc is None:
            return default
        return self.arc.get_current_val(name, default)


    def get_component_val(self, name, comp_name, default=None):
        """ Get component value of named control
        Get value from widget, if present, else use entry value
        """
        if self.arc is None:
            return default
        return self.arc.get_component_val(name, comp_name, default)

    def get_component_next_val(self, base_name,
                            nrange=50,
                            inc_dir=1,
                            default_value=None):
        """ Next value for this component
        :control_name: control name
        :comp_name: component name
        :nrange: - number of samples for incremental
        :default_value: default value
        """
        return self.arc.get_component_next_val(base_name,
                                nrange=nrange, inc_dir=inc_dir, default_value=default_value)


    def get_inc_val(self, name, default):
        """ Get inc value.  If none return default
        """
        if self.arc is None:
            return default
        return self.arc.get_inc_val(name, default)
 

    def set_current_val(self, name, val):
        """ Set current value.
        """
        if self.arc is None:
            return
        return self.arc.set_current_val(name, val)
 

    def set_component_val(self, name, comp_name, val):
        """ Set current value.
        """
        if self.arc is None:
            return
        return self.arc.set_component_val(name, comp_name, val)
        
    
    def set_call(self, name, function):
        """ Set for call back from arrange control
           1. If arc present via arc
           2. Else store for later enabling when arc is created
        """
        if self.arc is not None:
            self.arc.set_call(name, function)
        else:
            self.arc_call_d[name] = function
 
        

    def trace_control(self):
 
        def report_change(flag, val, cklist=None):
            SlTrace.lg("changed: %s = %d" % (flag, val), "controls")
            new_val = SlTrace.getLevel(flag)
            SlTrace.lg("New val: %s = %d" % (flag, new_val), "controls")
            if cklist is not None:
                cklist.list_ckbuttons()
        
        if self.tc is not None:
            self.tc.delete_tc_window()
            self.tc = None
        
        self.tc = TraceControlWindow(self, change_call=report_change)


    def tc_destroy(self):
        """ Called if TraceControlWindow window closes
        """
        self.tc = None


    def update_form(self):
        """ Update any field changes
        """
        if self.arc is not None:
            self.arc.update_form()
#########################################################################
#          Self Test                                                    #
#########################################################################
if __name__ == "__main__":
    from trace_control_window import TraceControlWindow    
        
    # root window created. Here, that would be the only window, but
    # you can later have windows within windows.
    mw = tk.Tk()
    def user_exit():
        print("user_exit")
        exit()
        
    SlTrace.setProps()
    SlTrace.setFlags("flag1=1,flag2=0,flag3=1,flag4=0, flag5=1, flag6=1")
        
    mw.geometry("400x300")
    
    #creation of an instance
    app = BlockWindow(mw,
                    title="select_window Testing",
                    pgmExit=user_exit,
                    )
    

    
    #mainloop 
    mw.mainloop()  

