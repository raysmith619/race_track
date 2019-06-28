# block_text.py        

from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock


   
class BlockText(BlockBlock):
    """
    Place text at position
        """
            
    def __init__(self,
                 text=None,
                 font_name="Tahoma",
                 font_size=12,
                 **kwargs):
        """ Setup object
        :text: text string to display
        :font_name: font name default: system font
        :font_size: font size default:12
        """
        super().__init__(**kwargs)
        if text is None:
            raise SelectError("Required text parameter is missing")
        
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        if self.height is None:     # TBD font specific
            self.height = .03
        if self.width is None:
            self.width = self.height*.5*len(text)
 
    def display(self):
        """ Display text in canvas
        """
        text_pos = self.get_absolute_point(Pt(0.,0.))
        text_coords = self.pts2coords(text_pos)
        text_x = int(text_coords[0])
        text_y = int(text_coords[1])
        canvas = self.get_canvas()
        text = self.text
        font_name = self.font_name
        font_size = self.font_size
        if len(self.xkwargs) == 0:
            self.xkwargs['anchor'] = "sw"
        self.text_tag = canvas.create_text(text_x, text_y,
                            font=(font_name, font_size),
                            text=text, **self.xkwargs) 
       
        
    
        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    from block_panel import BlockPanel
    
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
        
    bP = BlockBlock(canvas=canvas, width=th_width, height=th_height,
                   position=position,
                   cv_width=width, cv_height=height,
                   rotation=rotation)
    bP.display()

    text_pos = Pt(.9,.9)
    text_pi_x = 0
    text_pi_y = -.1
    text_box = BlockText(container=bP, text="text here:%s" % text_pos, position=text_pos)
    bP.comps.append(text_box)
    bP.display()
    
    mainloop()    
    