# block_check.py        

from enum import Enum
import copy
from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType,tran2matrix
from block_polygon import BlockPolygon


   
class BlockArrow(BlockPolygon):
    """
    Arrow for things like track road arrangement indicators
    +--------+--------+--------+--------+
    :        :        # (.5,1.):        :
    :        :       #:#       :        :
    :        :      # : #      :        :
    :        :     #  :  #     :        :
    :        :    #   :   #    :
    +--------+---#----+----#---+--------+
    :        :  #     :     #  :
    :        : #      :      # :        :
    :        :#       :       #:        :
    : (lx,cy)# (.4,.5): (.6,.5)#        :
    : (0,.5)#######   :   ####### (1,.5):
    +--------+----#---+---#-------------+
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    +--------+----#########----+--------+
    (blx, by)(.4,0)    (brx,by)(.6,0)
    """
            
    def __init__(self,
                 container=None,
                 modifier=None,
                 **kwargs):
        """ Arrow
        """
        if container is None:
            raise SelectError("BlockArrow is missing required container parameter")
        self.modifier = modifier        # Save for checking
        lx = 0.    # left point
        rx = 1.     # Right point
        mx = .5     # Middle x
        ty = 1.
        cy = .5     # Middle cross
        blx = .4
        brx = .6    # right x base
        by = 0.
        points = [Pt(blx,by), Pt(blx,cy),   # Left base vertical
                  Pt(lx, cy),              # left cross
                  Pt(mx, ty),               # left slant
                  Pt(rx, cy),               # Right slant
                  Pt(brx, cy),              # Right cross
                  Pt(brx, by)]               # Right base vertical

        xkwargs = {'outline' : True,
                   'width' : 3}                
        super().__init__(points=points, container=container, **kwargs)


    def get_modifier(self):
        """ Get modifier for road
        :returns: modifier string
        """
        return self.modifier


    def get_road_track(self):
        """ To allow being used as a "road" component
        in track_adjustments
        """
        return self.container
    

if __name__ == "__main__":
    from tkinter import *
    
    def test1():    
        from block_block import BlockBlock
        from block_text import BlockText
        
        width = 600
        height = 600        
        frame = Frame(width=width, height=height, bg="", colormap="new")
        frame.pack()
        canvas = Canvas(frame, width=width, height=height)
        canvas.pack()
        position = Pt(.5,.5)
        rotation = None
        th_width = 1.
        th_height = 1.   
        bP = BlockBlock(canvas=canvas)
        bP = BlockBlock(canvas=canvas, width=th_width, height=th_height,
               position=position,
               cv_width=width, cv_height=height,
               rotation=rotation)
        bP.display()
        
        box_height = .14
        box_width = box_height
        colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        ang_inc = 45
        for nb in range(len(colors)):
            box_pos = Pt(box_width*nb,box_height*nb)
            box_rot = ang_inc*nb
            color = colors[nb]
            box = BlockArrow(container=bP, width=box_width, height=box_height, position=box_pos, rotation=box_rot, color=color)
            bP.comps.append(box)
        bP.display()
            
        mainloop()

    test1()
