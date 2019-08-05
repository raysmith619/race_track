# block_polygon.py        

from enum import Enum
import copy
from homcoord import *
from block_block import BlockBlock,BlockType,tran2matrix

from select_trace import SlTrace
from select_error import SelectError


   
class BlockArc(BlockBlock):
    """
    Basic figure pie shape
    """
            
    def __init__(self,
                 center=None,
                 radius=None,
                 start=None,
                 arc=360.,
                 **kwargs):
        """ Setup object
        :radius: fraction of container default=.5
        :center: position of center in block
                default Pt(width/2, height/2)
        :start: angle starting default=0 deg (up)
        :arc: arc in degrees default=360 deg (counter clockwise)

        Arc 0 deg == up, positive is counter clockwise
                                  
                            *    *    *
                      *          :          *
                  *              :              *
                                 :
               *                 :                 *
              *                  :                  *
                                 :     
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
             *<--position
             | <--- radius ----> |
             
             center = Pt(position.x + radius, position.y + radius
             position = Pt(center.x - radius, center.y - radius
             
    """
        if SlTrace.trace("test"):
            print()
        super().__init__(ctype=BlockType.ARC, **kwargs)
        width = self.width
        height = self.height
        if radius is None:
            if width is None:
                width = 1.
            radius = width/2.
        self.radius = radius

        if center is None:
            center = Pt(.5, .5)
        self.center = center
        if start is None:
            start = 0.
        self.start = start
        self.arc = arc
        pts = []
        nstep = 360         # TBD - uniform separation
        end_angle = self.start + self.arc
        inc_angle = (end_angle-self.start)/nstep
        rad = self.radius                # Circle centered in the middle
        ct = self.center
        pts.append(ct)
        for i in range(nstep+1):
            angle = self.start + i * inc_angle
            theta = radians(angle)          # In radians
            pt_x = rad * sin(theta)
            pt_y = rad * cos(theta)
            pt = Pt(ct.x+pt_x, ct.y+pt_y)
            pts.append(pt)
        self.points = pts


    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = super().__deepcopy__(memo)
        new_inst.center = self.center
        new_inst.points = []
        new_inst.points.extend(self.points)
        new_inst.radius = self.radius
        new_inst.start = self.start
        new_inst.arc = self.arc
                
        return new_inst

 
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
        ###SlTrace.lg("\ndisplay polygon points[%s]=%s" % (self.tag, self.points), "display_points")
        pts = self.get_absolute_points()
        coords = self.pts2coords(pts)
        if SlTrace.trace("display"):
            SlTrace.lg("tag_list: %s" % self.get_tag_list())
            if self.position is not None:
                SlTrace.lg("center=%s" % self.center)
            if self.radius is not None:
                SlTrace.lg("radius=%.1g" % self.radius)
            if self.start is not None:
                SlTrace.lg("start=%.1f" % self.start)
            if self.arc is not None:
                SlTrace.lg("arc=%.1f" % self.arc)
            SlTrace.lg("arc: create_polygon(points:%s" % (pts), "arc_points")
            SlTrace.lg("create_polygon:%s, kwargs=%s" % (coords, self.xkwargs), "arc_coords")
        if self.xkwargs is None:
            self.xkwargs = {}
        if self.color is not None:
            self.xkwargs['fill'] = self.color
        if self.is_selected():
            self.xkwargs['outline'] = "red"
            self.xkwargs['width'] = 3
        else:
            self.xkwargs['outline'] = None
            self.xkwargs['width'] = None
            
        self.remove_display_objects()           # Remove display objects
        tag = self.get_canvas().create_polygon(coords, **self.xkwargs)
        self.store_tag(tag)
