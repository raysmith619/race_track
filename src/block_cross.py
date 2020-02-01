# block_cross.py        

from enum import Enum
import copy
from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType,tran2matrix
from block_pointer import AdjChoice
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
        self.lx = lx = 0.    # left point
        self.rx = rx = 1.     # Right point
        self.mx = mx = .5     # Middle x
        self.ty = ty = 1.
        self.mly = mly = .4    # middle lower y
        self.muy = muy = .6    # middle upper y
        self.blx = blx = .4
        self.brx = brx = .6    # right x base
        self.by = by = 0.
        points = [Pt(self.blx,by), Pt(self.blx,mly),   # Left base vertical
                  Pt(self.lx, self.mly),                # left cross lower
                  Pt(self.lx, self.muy),               # left cross vertical
                  Pt(self.blx, self.muy),               # left cross upper
                  Pt(self.blx, self.ty),                # left middle vertical
                  Pt(self.brx, self.ty),                # top cross
                  Pt(self.brx, self.muy),               # right upper vertical
                  Pt(self.rx, self.muy),                # right cross
                  Pt(self.rx, self.mly),                # right cross vertical
                  Pt(self.brx, self.mly),               # right lower cross
                  Pt(self.brx, self.by)]               # right lower vertical

        xkwargs = {'outline' : True,
                   'width' : 3}                
        super().__init__(points=points, container=container, **kwargs)
    
    
    def get_adj_coords(self, choice=AdjChoice.FORWARD):
        """ Return cursor coordinates to place for choice
        :choice: adjustment choice
        """
        if choice == AdjChoice.FORWARD:
            ip = Pt(self.mx, (self.muy+self.ty)/2)
        else:
            raise SelectError("Unexpected get_adj_coords choice: %s" % choice)
        coords = self.get_coords(ip)
        return coords
    


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
