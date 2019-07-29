# test_relative_points.py
"""
Verify:
    1. get_relative_point(0,0) == position
    
"""
from homcoord import *
import sys, traceback
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock
from block_text import BlockText
from block_arrow import BlockArrow

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
def mkpoint(x,y, rad=5, color="red"):
    """
    :rad:  radius of point
    """
    x0 = x-rad
    y0 = y-rad
    x1 = x+rad
    y1 = y+rad
    canvas.create_oval(x0,y0,x1,y1, fill=color)
    
def infront_coords(box):
    """ Adhock "infront point"
    
    :return coordinates (within candidate block)
    simulate Pt(.5, 1.1) which doesn't seem to work
    """
    pps = box.get_perimeter_abs_points()
    top_middle_pt = Pt((pps[1].x + pps[2].x)/2., (pps[1].y + pps[2].y)/2.)
    SlTrace.lg("top_middle_pt: %s" % top_middle_pt)
    infront_pt = Pt(top_middle_pt.x, top_middle_pt.y+box.get_length()*.1)
    SlTrace.lg("infront_pt: %s" % infront_pt)
    infront_coords = box.get_coords(infront_pt)
    return infront_coords
   
   
for nb in range(len(colors)):
    box_pos = Pt(box_width*nb,box_height*nb)
    box_rot = ang_inc*nb
    color = colors[nb]
    box = BlockArrow(container=bP, width=box_width, height=box_height,
                    position=box_pos, rotation=box_rot, color=color)
    box_pos = box.get_absolute_position()
    SlTrace.lg("\n%d: box_pos: %s" % (nb, box_pos))
    box_pos_coords = box.pts2coords(box_pos)
    SlTrace.lg("%d: box_pos_coords: %s" % (nb, box_pos_coords))
    box_internal_points = box.get_perimeter_points()
    SlTrace.lg("box: perimeter internal points %s" % box_internal_points)
    SlTrace.lg("box: perimeter relative points %s" % box.get_relative_points(box_internal_points))
    box_perimeter_points = box.get_perimeter_abs_points()
    SlTrace.lg("box: perimeter abs points: %s" % box_perimeter_points)
    box_perimeter_coords = box.get_perimeter_coords()
    in_front_coords = infront_coords(box)
    SlTrace.lg("infront coords: %s" % (in_front_coords))
    
    canvas.create_polygon(box_perimeter_coords, fill="", outline="black")
    mkpoint(box_pos_coords[0],box_pos_coords[1], color="red")
    mkpoint(in_front_coords[0],in_front_coords[1], color="green")
    c2 = box_perimeter_coords[2:4]
    mkpoint(c2[0],c2[1], color="blue")
    c3 = box_perimeter_coords[4:6]
    mkpoint(c3[0],c3[1], color="yellow")
    
    bP.comps.append(box)
bP.display()
    
mainloop()
