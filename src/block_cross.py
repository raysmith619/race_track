# block_cross.py        

from enum import Enum
import copy
from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType,tran2matrix
from block_polygon import BlockPolygon


   
class BlockCross(BlockPolygon):
    """
    cross for things like track road arrangement indicators
    
                 .4,1     .6,1
    +--------+--------+--------+--------+
    :        :    #########    :        :
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    :        :    #   :   #    :
    +--------+----#----+--#----+--------+
 0,.6 #############   :   ############# (1,.6):
    :        :        :        :        :
    :        :        :        :        :
    :        :        :        :        :
    :        :        :        :        :
 0,.4 #############   :   ############# (1,.4):
    +--------+----#---+---#-------------+
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    +--------+----#########----+--------+
                 .4,0     .6,0
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
        mly = .4    # middle lower y
        muy = .6    # middle upper y
        blx = .4
        brx = .6    # right x base
        by = 0.
        points = [Pt(blx,by), Pt(blx,mly),   # Left base vertical
                  Pt(lx, mly),                # left cross lower
                  Pt(lx, muy),               # left cross vertical
                  Pt(blx, muy),               # left cross upper
                  Pt(blx, ty),                # left middle vertical
                  Pt(brx, ty),                # top cross
                  Pt(brx, muy),               # right upper vertical
                  Pt(rx, muy),                # right cross
                  Pt(rx, mly),                # right cross vertical
                  Pt(brx, mly),               # right lower cross
                  Pt(brx, by)]               # right lower vertical

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
            box = BlockCross(container=bP, width=box_width, height=box_height, position=box_pos, rotation=box_rot, color=color)
            bP.comps.append(box)
        bP.display()
            
        mainloop()

    test1()
