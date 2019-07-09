# road_turn.py        
"""
Road turning block
"""
import copy
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock, BlockType
from block_arc import BlockArc
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
      arc   Turn's arc, in degrees e.g. -90 ==> 90 degree right turn
         
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
    """
    
            
    def __init__(self,
                track=None,
                radius=None,
                arc=90.,
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
        super().__init__(track, road_type=RoadType.TURN, **kwargs)
        tag = self.tag
        if self.width is None:
            self.width = self.height = self.get_road_width()
        if radius is None:
            radius = self.width
        self.radius = radius
        self.arc = arc
        if arc <= 0:
            arc_cent = Pt(0,0)
        else:
            arc_cent = Pt(1,0)
        turn = BlockArc(container=self,
                            tag=tag,
                            ###rotation=self.rotation-90,
                            center=arc_cent,
                            radius=1,
                            arc=arc,
                            xkwargs={'fill' : 'black'})
        self.comps.append(turn)
        
        
    def get_arc(self):
        """ Return turn arc
        """
        return self.arc
    
    
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
        