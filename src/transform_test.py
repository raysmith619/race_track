# transform_test.py
"""
Testing / proving 2D transformation ideas
"""        
import os
import sys
from tkinter import *    
import argparse

from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock

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

h = 200.
w = 10.
px = w
py = w
p1 = Pt(px,py)
p2 = Pt(px, py+h)
p3 = Pt(px+w, py+h)
p4 = Pt(px+w, py)

pts = [p1, p2, p3, p4]
coords = bP.pts2coords(pts)
canvas.create_polygon(coords, fill="red")
bP.display()

tran1 = Pt(h,h/2)
###tran1 = None
rot1 = -30.
###rot1 = None
scale1 = Pt(.5 , .5)
###scale1 = None
xtran1 = BlockBlock.xtran(translate=tran1, rotate=rot1, scale=scale1)
pts1 = BlockBlock.transform_points(xtran1, pts)
coords1 = bP.pts2coords(pts1)
canvas.create_polygon(coords1, fill="orange")
bP.display()

tran2 = Pt(h/2,h/3)
###tran1 = None
rot2 = 30.
###rot1 = None
scale2 = Pt(1.5 , 1.5)
xtran2 = BlockBlock.xtran(translate=tran2, rotate=rot2, scale=scale2)
pts1t2 = BlockBlock.transform_points([xtran1,xtran2], pts)
coords1t2 = bP.pts2coords(pts1t2)
canvas.create_polygon(coords1t2, fill="green")
bP.display()

   
mainloop()    
    