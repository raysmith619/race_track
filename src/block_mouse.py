# block_mouse.py        
"""
Interface for mouse operation support
"""

from select_trace import SlTrace
from select_error import SelectError
from mouse_info import MouseInfo
           
class BlockMouse:
    """ Mouse operation support
    """
            
    def __init__(self, bind_key=True):
        """ Setup
        :bind_key: process key press/release
                default: True - yes
        """
        self.motion_bind_id = None
        self.canvas.bind ("<ButtonPress-1>", self.mouse_down)
        self.canvas.bind ("<ButtonRelease-1>", self.mouse_up)
        self.canvas.bind ("<ButtonPress-2>", self.mouse2_down)
        self.canvas.bind ("<ButtonRelease-2>", self.mouse2_up)
        self.canvas.bind ("<ButtonPress-3>", self.mouse3_down)
        self.canvas.bind ("<ButtonRelease-3>", self.mouse3_up)
        self.canvas.bind ( "<Enter>", self.mouse_enter)
        self.canvas.bind ("<Leave>", self.mouse_leave)
        self.canvas.bind("<B1-Motion>", self.mouse_motion)
        self.canvas.bind("<B2-Motion>", self.mouse2_down_motion)
        self.canvas.bind("<B3-Motion>", self.mouse3_down_motion)
        self.mw.bind("<Motion>", self.motion)       # For generated events
        self.bind_key = bind_key
        if bind_key:
            self.mw.bind("<Key>", self.key_down)
            self.mw.bind("<KeyRelease>", self.key_release)
        self.mouse_info = MouseInfo(x_coord=0, y_coord=0)
        self.mouse2_info = MouseInfo(x_coord=0, y_coord=0)
        self.mouse3_info = MouseInfo(x_coord=0, y_coord=0)
        

    def get_info(self, mouse_no=1, event=None):
        """ Get mouse info
        :mouse_no:  mouse in action default: 1 (Left mouse)
        :event: mouse event, to update mouse_info
                default: no update
        :returns: MouseInfo, update if event present
        """
        if mouse_no == 1:
            info = self.mouse_info
        elif mouse_no == 2:
            info = self.mouse2_info
        elif mouse_no == 3:
            info = self.mouse3_info
        else:
            raise SelectError("%d - unrecognized mouse number"
                               % mouse_no)
            
        if event is not None:
            info.event = event  # Trace for analysis
            info.x_coord_prev = info.x_coord
            info.x_coord = event.x
            info.y_coord_prev = info.y_coord
            info.y_coord = event.y
        return info
    
    
    def key_down(self, event):
        SlTrace.lg("key_down - SHOULD BE OVERRIDDEN")
        
        
    def key_release(self, event):
        SlTrace.lg("key_release - SHOULD BE OVERRIDDEN")
        
        
    def mouse_down (self, event):
        self.get_info(mouse_no=1, event=event)
        pass
        
    def mouse2_down (self, event):
        self.get_info(mouse_no=2, event=event)
        pass
        
    def mouse3_down (self, event):
        self.get_info(mouse_no=2, event=event)
        pass

        
    def mouse_motion (self, event):
        """ mouse motion
        OVERRIDDEN
        """
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("move to x=%d y=%d" % (x,y), "motion_to")

    def mouse_down_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("move to x=%d y=%d" % (x,y), "motion_to")

        
    def mouse2_down_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("move2 to x=%d y=%d" % (x,y), "motion_to")

        
    def mouse3_down_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("move3 to x=%d y=%d" % (x,y), "motion_to")

    
    def mouse_enter (self, event):
        SlTrace.lg("enter", "enter")
        self.inside = True
        self.motion_bind_id = self.canvas.bind("<Motion>", self.mouse_motion)
                    

    
    def mouse_leave (self, event):
        SlTrace.lg("leave", "leave")
        self.inside = False
        if hasattr(self, 'motion_bind_id') and self.motion_bind_id is not None:
            self.canvas.unbind ("<Motion>", self.motion_bind_id)
            self.motion_bind_id = None

    def motion(self, event):
        cnv = event.widget
        ###x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        x = event.x
        y = event.y
        SlTrace.lg("motion to x=%d y=%d" % (x,y), "motion")
        
        
    def mouse_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("move to x=%d y=%d" % (x,y), "motion_to")
                            
    def mouse_up (self, event):
        self.is_down = False
        ###event.widget.itemconfigure (tk.CURRENT, fill =self.defaultcolor)
        cnv = event.widget
        x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("up at x=%d y=%d" % (x,y), "motion")
        SlTrace.lg("up is ignored", "motion")
        return
                            
    def mouse2_up (self, event):
        self.is_down = False
        ###event.widget.itemconfigure (tk.CURRENT, fill =self.defaultcolor)
        cnv = event.widget
        x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("up2 at x=%d y=%d" % (x,y), "motion")
        SlTrace.lg("up2 is ignored", "motion")
        return
                            
    def mouse3_up (self, event):
        self.is_down = False
        ###event.widget.itemconfigure (tk.CURRENT, fill =self.defaultcolor)
        cnv = event.widget
        x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("up3 at x=%d y=%d" % (x,y), "motion")
        SlTrace.lg("up3 is ignored", "motion")
        return
