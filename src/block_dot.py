# block_dot.py        

from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock


   
class BlockDot(BlockBlock):
    """
    Place dot at position, No local translation
    width is in pixels
        """
            
    def __init__(self,
                 color="red",
                 **kwargs):
        """ Setup object
        """
        super().__init__(**kwargs)
        self.color = color

    def display(self):
        """ Display text in canvas
        """
        pos = self.position
        comp = self
        if comp.container is not None:
            comp = comp.container
        
        dot_pos = comp.get_absolute_point(pos)
        dot_coords = self.pts2coords(dot_pos)
        dot_x = int(dot_coords[0])
        dot_y = int(dot_coords[1])
        canvas = self.get_canvas()
        dot_rad = 10
        dot_coord = [dot_x-dot_rad, dot_y-dot_rad, dot_x+dot_rad, dot_y+dot_rad]
        self.canvas_tag = canvas.create_oval(dot_coord, fill=self.color, **self.xkwargs) 
       
        
    
        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    from road_track import RoadTrack
    
    width = 600     # Window width
    height = width  # Window height
    rotation = None # No rotation
    pos_x = None
    pos_y = None
    parser = argparse.ArgumentParser()
    dispall = False      # Display every change
    
    parser.add_argument('--width=', type=int, dest='width', default=width)
    parser.add_argument('--height=', type=int, dest='height', default=height)
    parser.add_argument('--pos_x=', type=float, dest='pos_x', default=pos_x)
    parser.add_argument('--pos_y=', type=float, dest='pos_y', default=pos_y)
    parser.add_argument('--rotation=', type=float, dest='rotation', default=rotation)
    args = parser.parse_args()             # or die "Illegal options"
    
    width = args.width
    height = args.height
    pos_x = args.pos_x
    pos_y = args.pos_y
    rotation = args.rotation
    
    SlTrace.setFlags("short_points")
    SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
    SlTrace.lg("args: %s\n" % args)
    
            
    frame = Frame(width=width, height=height, bg="", colormap="new")
    frame.pack()
    canvas = Canvas(frame, width=width, height=height)
    canvas.pack()   
    th_width = 1.
    th_height = 1.
    position = None
    if pos_x is not None or pos_y is not None:
        if pos_x is None:
            pos_x = 0.
        if pos_y is None:
            pos_y = 0.
        position = Pt(pos_x, pos_y)
        
    tR = RoadTrack(tag="road_track",
                   canvas=canvas, width=th_width, height=th_height,
                   position=position,
                   cv_width=width, cv_height=height,
                   rotation=rotation)
    tR.display()

    text_pos = Pt(.9,.9)
    text_pi_x = 0
    text_pi_y = -.1
    text_box = BlockText(container=tR, text="text here", position=text_pos)
    tR.comps.append(text_box)
    tR.display()
    
    mainloop()    
    