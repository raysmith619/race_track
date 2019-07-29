# road_turn.py        
"""
Road turning block
"""
import copy
from math import *
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock, BlockType
from block_arc import BlockArc
from block_ring import BlockRing
from road_block import RoadBlock, RoadType
   
class RoadTurn(RoadBlock):
    """
    Standard road turn
    which can be used in constructing a road layout
      start    Pt()  within container
      width    road width usually defaulting to track road width
      radius   Outside radius of turn
      
      direction    Direction, in degrees counter clockwise, of
                  road at turn's start
      arc   Turn's arc, in degrees e.g. -90 ==> 90 degree left turn
         
         Right Turn      
 
                                  
                              *    *
                        *          *
                    *              *
                 *                 *
                *                  *
               *                   *
               *                   *
    position-> *********************
               | <-- road_width --> |


         Right Turn      
               (0,1)   *    *
                       *          *
                       *              *
                       *                 *
                       *                  *
                       *                   *
                       *                   *
    position-> (0,0)   ********************* (0,1)
                       | <-- road_width --> |



    """
    
            
    def __init__(self,
                track=None,
                radius=None,
                arc=-90.,
                **kwargs
                ):
        """ Setup object
        :track: Track object, container and controller of the road system
        :radius: radius, as fraction of container, to outside of road
                default: 1
        :arc: Amount, in degrees(counter clockwise), of circle default: 90 deg == left turn
        
        Create arc as polygon of points to facilitate coordinate transformation
        Arc = fraction of a circle with center at self.position, radius of self.radius
        line1: self.position to self.position + r-vector(r, angle=0)
        line2: self.position to self.position + r-vector(r, angle= arc)

        """
        self.arc = arc
        super().__init__(track, road_type=RoadType.TURN, **kwargs)
        tag = self.tag
        if self.width is None:
            self.width = self.height = self.get_road_width()
        if radius is None:
            radius = self.width
        self.radius = radius
        if arc >= 0:
            arc_cent = Pt(0,0)  # Left Turn
        else:
            arc_cent = Pt(1,0)  # Right Turn
        median_width = self.median_width
        median_x = self.median_x
        off_edge = self.off_edge
        edge_width = self.edge_width

        xkwargs = self.xkwargs
        if xkwargs is None:
            xkwargs = {'fill' : 'black'}
            
        turn = BlockArc(container=self,
                            tag=tag,
                            ###rotation=self.rotation-90,
                            center=arc_cent,
                            radius=1,
                            arc=arc,
                            xkwargs=xkwargs)
        self.comps.append(turn)

        median_strip = BlockRing(container=self,
                            tag=tag,
                            ###rotation=self.rotation-90,
                            center=arc_cent,
                            radius=median_x,
                            stripe_width=median_width,
                            arc=arc,
                            xkwargs={'fill' : 'yellow'})
        self.comps.append(median_strip)

        inner_edge = BlockRing(container=self,
                            tag=tag,
                            ###rotation=self.rotation-90,
                            center=arc_cent,
                            radius=off_edge,
                            stripe_width=edge_width,
                            arc=arc,
                            xkwargs={'fill' : 'white'})
        self.comps.append(inner_edge)
        
        outer_edge_width = edge_width
        outer_edge = BlockRing(container=self,
                            tag=tag,
                            ###rotation=self.rotation-90,
                            center=arc_cent,
                            radius=1-off_edge-outer_edge_width/2,
                            stripe_width=outer_edge_width,
                            arc=arc,
                            xkwargs={'fill' : 'white'})
        self.comps.append(outer_edge)
        
    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = super().__deepcopy__(memo)
        new_inst.arc = self.arc
        return new_inst


    def __str__(self):
        str_str = self.__class__.__name__ + " id:%s" % self.id
        if self.arc is not None:
            str_str += " arc:%.0f" % self.arc
        if hasattr(self, "origin") and self.origin is not None:
            str_str += " in:%s" % self.origin
        if hasattr(self, "state") and self.state is not None:
            str_str += " state:%s" % self.state
        return str_str

    def get_modifier(self):
        """ Get modifier for road
        :returns: modifier string
        """
        arc = self.get_arc()
        if arc > 0:
            return "left"
        else:
            return "right"


    def get_front_addon_rotation(self):
        """ Get rotation for a forward "addon" block
        :returns: rotation of addon block in containers reference
                    None if no rotation, treated as 0. deg
        """
        arc = self.get_arc()
        rotation = self.get_rotation()
        add_rot = (rotation + arc) % 360.
        if SlTrace.trace("get_front_addon"):
            tlc = self.get_relative_point(Pt(0,1))
            container = self.container if self.container is not None else self
            SlTrace.lg("get_front_addon_rotation %s = %.2f" % (self, add_rot))
        return add_rot


    def get_front_addon_position(self):
        """ Get point on which to place a forward "addon" block
        :returns: point (Pt) in containers reference 
        """
        arc = self.get_arc()
        rotation = self.rotation
        if rotation is None:
            rotation = 0.
        if arc >= 0.:                   # Left turn ?
            base_add_pt = Pt(0,0)       # TBD Works only for 90 deg angles ???
        else:
            theta = radians(arc)   # Right turn
            base_add_pt = Pt(1-cos(theta), sin(-theta))
        add_pt = self.get_relative_point(base_add_pt)
        if SlTrace.trace("get_front_addon"):
            container = self.container if self.container is not None else self
            SlTrace.lg("get_front_addon_position %s = %s(%s)" %
                        (self, add_pt, self.container.get_absolute_point(add_pt)))
        return add_pt
        
        
    def get_arc(self):
        """ Return turn arc
        """
        return self.comps[0].arc
    
    
    def new_arc(self, arc):
        """ Change arc of turn
         No change to selected state(s)
        :arc: new arc
        """
        len_comps = len(self.comps)
        if len_comps != 1:
            raise SelectError("len(RoadTurn.comps)(%d) != expected(1)" % len_comps)
        old_arc = self.comps[0]
        old_arc.remove_display_objects()        # Remove old_arc from display
        new_arc = BlockArc(container=self,
                           tag=old_arc.tag,
                            ###rotation=self.rotation-90,
                            center=old_arc.center,
                            radius=old_arc.radius,
                            arc=arc,
                            xkwargs=old_arc.xkwargs)
        self.comps[0] = new_arc


    def get_length_dist(self):
        """ Determine traversal length for the road in terms of fraction of container
        Treat the distance as the outside perimeter of the arc
        """
        arc = self.get_arc()
        radius = self.get_length()
        dist = radius*2*pi*arc/360.
        return dist
        