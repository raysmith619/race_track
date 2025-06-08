# block_line.py     05Jun2025  crs, from block_polygon.py        

from enum import Enum
import copy
from homcoord import *
from block_block import BlockBlock,BlockType,tran2matrix

from select_trace import SlTrace
from select_error import SelectError


   
class BlockLine(BlockBlock):
    """
    Basic line to be component of BlockBlock
    Avoid filling
    """
            
    def __init__(self,
                 ctype=BlockType.LINE,
                 points=None,
                 line_width=None,
                 **kwargs):
        """ Setup object
        :points:    points, used for this component
        :line_width: line width so not to be confused
                    with block width
            default=passed to tkinter/GUI
        :All other BlockBlock parameters:
        """
        super().__init__(ctype=ctype, **kwargs)
        self.points = points
        self.line_width=line_width


    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = super().__deepcopy__(memo)
        new_inst.points = []
        for point in self.points:
            new_inst.points.append(point)
                
        return new_inst


 
    def display(self):
        """ Display line
        The line consists of a list of points
        whose position must be transformed though
        the coordinates of each of the enclosing
        components.
        Each of the components, upon creation,
        stored a translation matrix in .xtran.
        
        We will create a single translation matix
        by composing the individual translation
        matrixes from the top container.
        """
        canvas = self.get_canvas()
        if canvas is None:
            raise SelectError("NO canvas")
            
        if SlTrace.trace("display_line"):
            if len(self.points) < 10 and SlTrace.trace("short_points"):
                SlTrace.lg("\ndisplay line points[%s]=%s" % (self.tag, self.points))
            elif SlTrace.trace("display_points"):            
                SlTrace.lg("\ndisplay line points[%s]=%s" % (self.tag, self.points))
            SlTrace.lg("tag_list: %s" % self.get_tag_list())    
        if SlTrace.trace("display_line"):
            if self.position is not None:
                SlTrace.lg("position=%s" % self.position)
            if self.rotation is not None:
                SlTrace.lg("rotation=%.1fdeg" % self.rotation)
        pts = self.get_absolute_points()
        coords = self.pts2coords(pts)

        if SlTrace.trace("display_line"):
            if len(pts) < 10 and SlTrace.trace("short_points"):
                SlTrace.lg("display_line(absolute points:%s" % (pts))
            elif SlTrace.trace("display_points"):
                SlTrace.lg("display_line(absolute points:%s" % (pts))
            if len(pts) < 10 and SlTrace.trace("short_points"):
                SlTrace.lg("display_line(coords:%s, kwargs=%s" % (coords, self.xkwargs))
            elif  SlTrace.trace("display_points"):
                SlTrace.lg("display_line(coords:%s, kwargs=%s" % (coords, self.xkwargs))
        if self.color is not None and not hasattr(self.xkwargs, 'fill'):
            self.xkwargs['fill'] = self.color                   # Use color if specified and not overridden
        
        self.remove_display_objects()    
        tag = canvas.create_line(coords, width=self.line_width, **self.xkwargs)
        self.store_tag(tag)
        


def add_line(container,
             tag=None,
             points=None,
             position=None,
             line_width=None,
             rotation=None,
             velocity=None,
             visible=True,
             display=True,
             **kwargs):
    """ Add another line to block component
    :tag: optional descriptive tag
        default: "'line':" + "kwargs:fill"
    :line_width: line width
    :display: Display after addition
            default: True
    :kwargs: arguments to Tkinter.create_line
    """
    if tag is None:
        tag = "line"
        
    SlTrace.lg("\nadd_line points=%s" % points)
    if position is not None:
        SlTrace.lg("position=%s" % position)
    if rotation is not None:
        SlTrace.lg("rotation=%.1fdeg" % rotation)
    comp = BlockLine(tag=tag,
                      container=container,
                      position=position,
                      line_width=line_width,
                      rotation=rotation,
                      velocity=velocity,
                      points=points,
                      xkwargs=kwargs)
    SlTrace.lg("_m:%s" % tran2matrix(comp.base_xtran()))
    container.add_components(comp)
    if display:
        container.display()
    SlTrace.lg("component Added")

        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    def test1():
        width = 600     # Window width
        height = width  # Window height
        rotation = -45.
        pos_x = .15
        pos_y = .08
        parser = argparse.ArgumentParser()
        
        parser.add_argument('--rotation=', type=float, dest='rotation', default=rotation)
        parser.add_argument('--pos_x=', type=float, dest='pos_x', default=pos_x)
        parser.add_argument('--pos_y=', type=float, dest='pos_y', default=pos_y)
        args = parser.parse_args()             # or die "Illegal options"
        
        pos_x = args.pos_x
        pos_y = args.pos_y
        
        SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
        SlTrace.lg("args: %s\n" % args)
        
                
        frame = Frame(width=width, height=height, bg="", colormap="new")
        frame.pack()
        canvas = Canvas(frame, width=width, height=height)
        canvas.pack()   
        th_width = 1.
        th_height = 1.
        bb = BlockBlock(canvas=canvas, width=th_width, height=th_height,
                        cv_width=width, cv_height=height)
        w = .05
        wbeg = th_width/2 - w/2
        wend = wbeg + w
        h = .8
        hbeg = th_height/2 - h/2
        hend = hbeg + h
        SlTrace.lg("Thin bar w=%g, h=%g" % (w, h))
        p1 = Pt(wbeg, hbeg)
        p2 = Pt(wbeg, hend)
        p3 = Pt(wend, hend)
        p4 = Pt(wend, hbeg)
        pts = [p1, p2, p3, p4]
        
        cur_pos_x = pos_x
        cur_pos_y = pos_y
        cur_rot = rotation
        colors = ["red", "orange", "yellow", "green", "blue",
                  "indigo", "violet"]
        nstep = len(colors)
        inc_x = 2*pos_x/nstep
        inc_y = pos_y/nstep
        inc_rot = 90./nstep
        width = .25
        height = .25
        inc_w = width/nstep
        inc_h = width/nstep
        for i in range(nstep):
            n = i + 1
            cur_pos_x = pos_x + i*inc_x
            cur_pos_y = pos_y + i*pos_y
            cur_rot = rotation + i*inc_rot
            cur_width = width + i*inc_w
            cur_height = height + i*inc_h
            SlTrace.lg("\n%d: %s pos(%.2f,%.2f) width(%.2f, %2f) rot(%.2f)deg" %
                       (n, colors[i], cur_pos_x,cur_pos_y, cur_width, cur_height, cur_rot))
            add_line(bb, points=pts,
                     line_width=i+1,
                    fill = colors[i],
                    position = Pt(cur_pos_x, cur_pos_y),
                    rotation = cur_rot,
                    )
    
        add_line(bb, points=pts,
                    fill="black",
                    rotation=rotation,
                    position=Pt(pos_x+inc_x, pos_y),
                    )
    
        bb.display()

        '''
        points = [Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)]
        bb = BlockLine(rotation=45.,
                          points=points)
    
        print("points=%s" % bb.points)
        
        pts2 = bb.get_relative_points()
        print("points2=%s" % pts2)
        '''
        
        
        mainloop()
        
    test1()