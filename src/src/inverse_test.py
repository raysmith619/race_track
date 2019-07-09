import os
import sys
from tkinter import *    
import argparse

from block_panel import BlockPanel

from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,tran2matrix
from block_polygon import BlockPolygon

width = 600     # Window width
height = width  # Window height
rotation = None # No rotation
pos_x = 100
pos_y = 200
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

###SlTrace.setFlags("short_points")
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

poly_pos = Pt(.4,.5)
poly_points = [Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)]
poly = BlockPolygon(container=bP, position=poly_pos, width=.5, height=.3, points=poly_points, xkwargs={'fill' : "red"})
bP.comps.append(poly)
bP.display()
SlTrace.lg("\npoly1 points: %s" % poly.get_absolute_points())
poly_xtran = poly.get_full_xtran()
SlTrace.lg("poly_xtran=%s" % tran2matrix(poly_xtran))
poly_ixtran = poly.get_full_ixtran()
SlTrace.lg("poly_ixtran=%s" % tran2matrix(poly_ixtran))
xtran_ti = poly_xtran * poly_ixtran
SlTrace.lg("xtran x ixtran=%s(%s)" % (tran2matrix(xtran_ti), xtran_ti))

poly2 = poly.dup()
poly2.xkwargs = {'fill' : "orange"}
poly2.drag_block(delta_x=-.2, delta_y=-.2, canvas_coord=False )
bP.comps.append(poly2)
SlTrace.lg("\npoly2 points: %s" % poly2.get_absolute_points())
bP.display()

poly3 = poly2.dup()
poly3.xkwargs = {'fill' : "blue"}
SlTrace.lg("\npoly3 points(before drag): %s" % poly3.get_absolute_points())
delta_x=50
delta_y=-100
canvas_coord=True 
SlTrace.lg("drag_block: delta_x,y(%d,%d) canvas_coord=%s" % (delta_x, delta_y, canvas_coord))
poly3.drag_block(delta_x=delta_x, delta_y=delta_y, canvas_coord=canvas_coord)
bP.comps.append(poly3)
SlTrace.lg("\npoly3 points(after drag): %s" % poly3.get_absolute_points())
bP.display()

mainloop()    
