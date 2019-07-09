# block_mouse.py        
"""
Interface for mouse operation support
"""

from select_trace import SlTrace
from select_error import SelectError
   
class BlockMouse:
    """ Mouse operation support
    """
            
    def __init__(self):
        """ Setup 
        """
        self.motion_bind_id = None
        self.canvas.bind ("<ButtonPress-1>", self.mouse_down)
        self.canvas.bind ("<ButtonRelease-1>", self.mouse_up)
        self.canvas.bind ( "<Enter>", self.mouse_enter)
        self.canvas.bind ("<Leave>", self.mouse_leave)
        self.canvas.bind("<B1-Motion>", self.mouse_down_motion)

    def mouse_down (self, event):
        if SlTrace.trace("part_info"):
            cnv = event.widget
            x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
            parts = self.get_parts_at(x,y)
            if parts:
                SlTrace.lg("x=%d y=%d" % (x,y))
                for part in parts:
                    SlTrace.lg("    %s\n%s" % (part, part.str_edges()))
        self.is_down = True
        if self.inside:
            SlTrace.lg("Click in canvas event:%s" % event, "motion")
            cnv = event.widget
            x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
            SlTrace.lg("x=%d y=%d" % (x,y), "down")

        
    def mouse_down_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("move to x=%d y=%d" % (x,y), "motion_to")

    
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
