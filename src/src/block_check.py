# block_check.py        

from enum import Enum
import copy
from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType,tran2matrix
from block_polygon import BlockPolygon


   
class BlockCheck(BlockBlock):
    """
    Checkered block - to demonstrate / investigate levels of composition
    +--------+--------+--------+--------+
    :        :########:        :########:
    :        :########:        :########:
    :        :########:        :########:
    :        :########:        :########:
    +--------+--------+--------+--------+
    :########:        :########:        :
    :########:        :########:        :
    :########:        :########:        :
    :########:        :########:        :
    +--------+--------+--------+--------+
    :        :########:        :########:
    :        :########:        :########:
    :        :########:        :########:
    :        :########:        :########:
    +--------+--------+--------+--------+
    :########:        :########:        :
    :########:        :########:        :
    :########:        :########:        :
    :########:        :########:        :
    +--------+--------+--------+--------+
    levels = 2
    nx = 2
    ny = 2
    fill1 = "white"
    fill2 = "lightgreen"
    """
            
    def __init__(self,
                 levels=2,   # First attempt - only one level
                 nx=2,
                 ny=2,
                 fill1 = "white",
                 fill2 = "lightgreen",
                 **kwargs):
        """ Setup object
        :levels: Number of levels
        :nx: number of divisions in x direction default: 2
        :ny: number of divisions in y direction default: nx
        :fill1: color to fill 1st square
        :fill2: color to fill alternating square
        """
        super().__init__(ctype=BlockType.COMPOSITE, **kwargs)
        inc_x = self.width / float(nx)
        inc_y = self.height / float(ny)
        pos_b = Pt(.5,.5)       # Hack to see it
        inc_x = .1      # HACK to see it !!!
        inc_y = .1
        fill_row_idx = 0        # Fill index alternates rows (bumped twice before use)
        square_points = [Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)]
        for i in range(nx):
            fill_row_idx += 1
            fill_col_idx = fill_row_idx
            pos_x = i * inc_x
            for j in range(ny):
                fill_col_idx += 1
                pos_y = j * inc_y
                pos_b = Pt(pos_x, pos_y)
                if fill_col_idx % 2 == 0:
                    fill = fill1
                else:
                    fill = fill2
                block = BlockPolygon(container=self, position=pos_b,
                                     width=inc_x, height=inc_y,
                                     points = square_points,
                                     xkwargs = {"fill" : fill})
                self.add_components(block)


    def display(self):
        for comp in self.comps:
            comp.display()

        self.task_update()
        SlTrace.lg("After check box display")
        