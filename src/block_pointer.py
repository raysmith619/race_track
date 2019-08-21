# block_pointer.py        

from enum import Enum
import copy
from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType,tran2matrix
from block_polygon import BlockPolygon

class AdjChoice(Enum):
    FORWARD = 1
    LEFT = 2
    RIGHT = 3
    BACKWARD = 4
    CHANGE = 5
   
class BlockPointer(BlockPolygon):
    """
   pointer for things like track road arrangement indicators
    
                 .4,1     .6,1
    +--------+---#-----+-----#---+--------+
    :        : #       :       # :        :
    :        #:        :         #        :        :
    :      # :         :           #      :
    :    #   :         :         :   #
    +--#------+--------+--#------+------#--+
 0,.6 #############   :   ############# (1,.6):
    :        :        :        :        :
    : left   :        :    right        :
    :        :        :        :        :
    :        :        :        :        :
    +--------+----#---+---#-------------+
    :        :        :        :        :
    :        :        :        :        :
    :        :        :        :        :
 0,.3 #############   :   ############# (1,.3):
    :        :    #   :   #    :        :
    :        :    # back  #    :        :
    :        :    #   :   #    :        :
    :        :    #   :   #    :        :
    +--------+----#########----+--------+
                 .3,0     .7,0
    """
            
    def __init__(self,
                 container=None,
                 modifier=None,
                 **kwargs):
        """ Arrow
        """
        if container is None:
            raise SelectError("BlockPointer is missing required container parameter")
        self.comps = []     # Optional extra parts
        self.modifier = modifier        # Save for checking
        self.lx = lx = 0.    # left edge
        self.rx = rx = 1.     # Right edge
        self.mx = mx = .5     # Middle x
        self.ty = ty = 1.
        self.mly = mly = .2    # middle lower y
        self.muy = muy = .6    # middle upper y
        self.blx = blx = .2
        self.brx = brx = .8    # right x base
        self.by = by = -.2          # Below (into road)
        points = [Pt(blx,by), Pt(blx,mly),   # Left base vertical
                  Pt(lx, mly),                # left cross lower
                  Pt(lx, muy),               # left point slant
                  Pt(mx, ty),                # Upper point
                  Pt(rx, muy),               # right point slant
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
    
    
    def highlight(self, x=None,  y=None, display=True):
        """ Hilight adjustment block
        :ck_block: adjustment block
        :x: x coordinate
        :y: y coordinate
        :display: display result default:
        """
        choice = AdjChoice.FORWARD
        if self.comps:
            for comp in self.comps:
                comp.remove_display_objects()
                del comp
            self.comps = []
            
        if not self.is_at(x,y):
            return
            
        self.xkwargs['activedash'] = 1
        self.xkwargs['activewidth'] = 1
        self.xkwargs['activeoutline'] = "red"
        #self.xkwargs['activefill'] = "gray"
        ip = self.get_internal_point([x,y])
        if (ip.y < self.mly and ip.y > self.by
            and ip.x > self.lx and ip.x < self.rx):
            choice = AdjChoice.BACKWARD
            if display:
                fp_points = [                           # Backward point
                            Pt(self.lx,self.mly),
                            Pt(self.rx, self.mly),        # rt upper pt
                            Pt(self.mx, self.by)          # middle pt
                            ]
                forward_point = BlockPolygon(container=self,
                                             points=fp_points,
                                             color="black")
                self.comps.append(forward_point)
        elif (ip.y < self.muy and ip.y > self.mly
            and ip.x > self.mx and ip.x < self.rx):
            choice = AdjChoice.RIGHT
            if display:
                right_points = [                         # Right point
                      Pt(self.mx, self.muy),               # left point slant
                      Pt(self.rx, (self.mly+self.muy)/2),                # Upper point
                      Pt(self.mx, self.mly),               # right point slant
                    ]
                right_ind = BlockPolygon(container=self,
                                             points=right_points,
                                             color="green")
                self.comps.append(right_ind)
        elif (ip.y < self.muy and ip.y > self.mly
            and ip.x > self.lx and ip.x < self.mx):
            choice = AdjChoice.LEFT
            if display:
                backward_points = [                         # Left point
                      Pt(self.mx, self.muy),               # right point slant
                      Pt(self.lx, (self.mly+self.muy)/2),                # Upper point
                      Pt(self.mx, self.mly),               # right point slant
                    ]
                right_ind = BlockPolygon(container=self,
                                             points=backward_points,
                                             color="blue")
                self.comps.append(right_ind)
        else:
            choice = AdjChoice.FORWARD
            if display:
                forward_points = [                         # Forward point
                      Pt(self.lx, self.muy),               # left point slant
                      Pt(self.mx, self.ty),                # Upper point
                      Pt(self.rx, self.muy),               # right point slant
                    ]
                backward_rect = BlockPolygon(container=self,
                                             points=forward_points,
                                             color="red")
                self.comps.append(backward_rect)
        if display:
            self.display()
        
        
        return choice


    def display(self):
        """ Display, including optional parts
        """
        super().display()
        for comp in self.comps:
            comp.display()


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
            box = BlockPointer(container=bP, width=box_width, height=box_height, position=box_pos, rotation=box_rot, color=color)
            bP.comps.append(box)
        bP.display()
            
        mainloop()

    test1()
