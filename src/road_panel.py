# road_panel.py        
"""
Basis of a road arrangement
Uses RoadBlock parts
"""
from enum import Enum
import copy
from homcoord import *
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError
from road_block import RoadBlock
from block_polygon import BlockPolygon

   
class RoadPanel(RoadBlock):
    """
    Block panel 
    which can be used to construct a road layout
    Object properties are expressed in relation to the containing object.
    """
    
            
    def __init__(self,
                container,
                background=None,
                **kwargs
                ):
        """ Setup object
        :background: background fill color
        """
        SlTrace.lg("RoadPanel: %s" % (self))
        super().__init__(container, **kwargs)
        if background is None:
            background = "lightgreen"
        self.background = background
        canvas = self.get_canvas()
        if canvas is None:
            self.canvas = Canvas(width=self.cv_width, height=self.cv_height)
        """ Do background / scenery
        """
        bk_inset = .0001
        ###bk_inset = 0.
        p1 = Pt(0,0)
        p2 = Pt(0,1)
        p3 = Pt(1,1)
        p4 = Pt(1,0)
        background = BlockPolygon(
                              points=[p1,p2,p3,p4], position=Pt(bk_inset,bk_inset),
                              container=self,
                              height = 1.0 - 2*bk_inset,
                              width = 1.0 - 2*bk_inset,
                              xkwargs={'fill' : self.background})
        self.comps.append(background)


    def get_absolute_points(self, points=None):
        if points is None:
            p1 = Pt(0,0)
            p2 = Pt(0,1)
            p3 = Pt(1,1)
            p4 = Pt(1,0)
            points = [p1,p2,p3,p4]
        return super().get_absolute_points(points)
    
        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    from block_text import BlockText
    from block_arc import BlockArc
    from block_dot import BlockDot
    
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
        
    bP = RoadPanel(container=None, canvas=canvas, width=th_width, height=th_height,
                   position=position,
                   cv_width=width, cv_height=height,
                   rotation=rotation)
    bP.display()

    circle_pos = Pt(.5,.5)
    circle = BlockArc(container=bP, width=.1, position=circle_pos)
    bP.comps.append(circle)
    bP.display()

    dot_pos = Pt(.25,.25)
    dot = BlockDot(container=bP, width=.1, position=dot_pos)
    bP.comps.append(dot)
    bP.display()
    
    
    text_pos = Pt(.7,.9)
    text_pi_x = 0
    text_pi_y = -.1
    text_box = BlockText(container=bP, text="text here:%s" % text_pos, position=text_pos)
    bP.comps.append(text_box)
    bP.display()
    
    do_off_page = True
    do_off_page = False
    if do_off_page:
        off_page_pos = Pt(100.,100.)
        off_page_box = BlockText(container=bP, text="Off page:%s" % (off_page_pos), position=off_page_pos)
        bP.comps.append(off_page_box)
        bP.display()
    
    mainloop()