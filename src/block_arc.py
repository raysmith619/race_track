# block_polygon.py        

from enum import Enum
import copy
from homcoord import *
from block_block import BlockBlock,BlockType,tran2matrix

from select_trace import SlTrace
from select_error import SelectError


   
class BlockArc(BlockBlock):
    """
    Basic figure to be component of BlockBlock
    """
            
    def __init__(self,
                 center=None,
                 radius=None,
                 start=None,
                 arc=360.,
                 **kwargs):
        """ Setup object
        :radius: fraction of container default=.5
        :start: angle starting default=0 deg (up)
        :arc: arc in degrees default=360 deg (counter clockwise)

        Arc 0 deg == up, positive is counter clockwise
                                  
                            *    *    *
                      *          :          *
                  *              :              *
                                 :
               *                 :                 *
              *                  :                  *
                                 :  position    
             *                   :  center           *
             *                   : /                 *
             *-------------------+-------------------*
             *                   :                   *
             *                   :                   *
              *                  :                  *
                                 :
                *                :                *
                  *              :              *
                      *          :          *
                            *    *    *

             | <--- radius ----> |
             
             center = Pt(position.x + radius, position.y + radius
             position = Pt(center.x - radius, center.y - radius
             
    """
        super().__init__(ctype=BlockType.ARC, **kwargs)
        width = self.width
        height = self.height
        if radius is not None:
            height = width = 2 * radius
        elif width is not None:
            radius = width/2
        else:
            raise SelectError("One of radius or width must be specified")

        self.radius = radius
        self.height = height
        self.width = width
        
        position = self.position
        if center is not None:
            position = center
        elif position is not None:
            center = position          # Place center up 1/2 to right 1/2
        else:
            raise SelectError("One of center or position must be specified")
        
        self.center = center
        self.position = position
        
        if start is None:
            start = 0.
        self.start = start
        self.arc = arc
        pts = []
        nstep = 360         # TBD - uniform separation
        end_angle = self.start + self.arc
        inc_angle = (end_angle-self.start)/nstep
        rad = .5                # Circle centered in the middle
        ct = Pt(0, 0)
        pts.append(ct)
        for i in range(nstep+1):
            angle = self.start + i * inc_angle
            theta = radians(-angle)          # In radians
            pt_x = rad * sin(theta)
            pt_y = rad * cos(theta)
            pt = Pt(ct.x+pt_x, ct.y+pt_y)
            pts.append(pt)
        self.points = pts
 
    def display(self):
        """ Display polygon
        The polygon consists of a list of points
        whose position must be transformed though
        the coordinates of each of the enclosing
        components.
        Each of the components, upon creation,
        stored a translation matrix in .xtran.
        
        We will create a single translation matix
        by composing the individual translation
        matrixes from the top container.
        """
        SlTrace.lg("\ndisplay polygon points[%s]=%s" % (self.tag, self.points), "display_points")
        SlTrace.lg("tag_list: %s" % self.get_tag_list())    
        
        if self.position is not None:
            SlTrace.lg("center=%s" % self.center)
        if self.radius is not None:
            SlTrace.lg("radius=%.1g" % self.radius)
        if self.start is not None:
            SlTrace.lg("start=%.1f" % self.start)
        if self.arc is not None:
            SlTrace.lg("arc=%.1f" % self.arc)
        pts = self.get_absolute_points()
        SlTrace.lg("arc: create_polygon(points:%s" % (pts), "arc_points")
        coords = self.pts2coords(pts)
        SlTrace.lg("create_polygon:%s, kwargs=%s" % (coords, self.xkwargs), "arc_coords")
        if self.xkwargs is None:
            self.xkwargs = {}
        self.get_canvas().create_polygon(coords, **self.xkwargs)
