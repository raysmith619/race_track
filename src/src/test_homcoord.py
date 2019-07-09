# test_homcoord.py        

import copy
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError
from matplotlib.backends.backend_pdf import fill


def coords2pts(coords):
    """ Convert Canvas coordinate list to list of
    homcord Pt()
    :coords: list of x1,y1,...xn,yn coordinates
    :returns: list of homcoord Pt()
    """
    points = []
    for x,y in coords:
        pt = Pt(x,y) 
        points.append(pt)
    return points


def pts2coords(pts):
    """ Convert homcoord points to Canvas coordinate list
    :pts: list of homcoord Pt()
    :returns: list of x1,y1,....xn,yn coordinates
    """
    coords = []
    for pt in pts:
        x, y = pt.xy 
        coords.extend([x,y])
    return coords
        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    
    width = 600     # Window width
    height = width  # Window height

    parser = argparse.ArgumentParser()
    
    parser.add_argument('--width=', type=int, dest='width', default=width)
    parser.add_argument('--height=', type=int, dest='height', default=height)
    args = parser.parse_args()             # or die "Illegal options"
    
    width = args.width
    height = args.height
    
    SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
    SlTrace.lg("args: %s\n" % args)
    
            
    frame = Frame(width=width, height=height, bg="", colormap="new")
    frame.pack()
    canvas = Canvas(frame, width=width, height=height)
    canvas.pack()
    canvas.create_rectangle(10, 10, width-10, height-10, fill="blue")   
    th_width = width
    th_height = height
    w = .8 * th_width
    wbeg = w/10
    wend = w + wbeg
    h = .8 *th_height
    hbeg = h/10
    hend = h - hbeg
    x_cent = (wbeg+wend)/2.
    y_cent = (hbeg+hend)/2.
    points=[[(wbeg+wend)/2.,hbeg],
            [wend,(hbeg+hend)/2],
            [(wbeg+wend)/2,hend],
            [wbeg, (hbeg+hend)/2],
           ]
    coords = []
    for point in points:
        coords.append(point[0])
        coords.append(point[1])
        
    canvas.create_polygon(coords, fill="red")
    pts = coords2pts(points)
    
    xft = Xlate(10, 20)
    pts2 = []
    for pt in pts:
        pt2 = xft.apply(pt)
        pts2.append(pt2)
        
    coords2 = pts2coords(pts2)
    canvas.create_polygon(coords2, fill="green")
        
    canvas.create_polygon(coords, fill="red")

    pts = coords2pts(points)    
    xfr = Xrotate(radians(10.))
    pts3 = []
    for pt in pts:
        pt3 = xfr.apply(pt)
        pts3.append(pt3)
        
    coords3 = pts2coords(pts3)
    canvas.create_polygon(coords3, fill="yellow")

    xfs = Xscale(1.2)
    pts4 = []
    for pt in pts3:
        pt4 = xfs.apply(pt)
        pts4.append(pt4)
        
    coords4 = pts2coords(pts4)
    canvas.create_polygon(coords4, fill="yellow")

    xfs = Xscale(.8)
    pts5 = []
    for pt in pts3:
        pt5 = xfs.apply(pt)
        pts5.append(pt5)
        
    coords5 = pts2coords(pts5)
    canvas.create_polygon(coords5, fill="orange")
    
    mainloop()