    

from tkinter import *
from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType,tran2matrix
from block_polygon import BlockPolygon


def dot_grid(box, nb):
    """ Do dot grid within box
    :box: box object within which to add dot grid
    :nb: pattern index 0...
    """
    from block_arc import BlockArc
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    mg = nb + 3     # Grid side number
    radius = .05
    for i in range(mg):
        for j in range(mg):
            position = Pt(i/mg, j/mg)
            icolor = max(i,j)
            color = colors[icolor%len(colors)] 
            ba = BlockArc(container=box, color=color, radius=radius, position=position)
            box.comps.append(ba)
    ###box.display()

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
    bP = BlockBlock(canvas=canvas, width=th_width, height=th_height,
           position=position,
           cv_width=width, cv_height=height,
           rotation=rotation)
    
    box_height = .14
    box_width = box_height
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    ang_inc = 45
    for nb in range(len(colors)):
        box_pos = Pt(box_width*nb,box_height*nb)
        box_rot = ang_inc*nb
        color = colors[nb]
        box1 = BlockBlock(container=bP, width=box_width, height=box_height, position=box_pos, rotation=box_rot)
        bP.comps.append(box1)
        box = BlockBlock(container=box1)
        box1.comps.append(box)
        dot_grid(box, nb)
    bP.display()
        
    mainloop()

test1()
