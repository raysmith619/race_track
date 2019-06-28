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
                default: self.road_width
        :arc: Amount, in degrees(counter clockwise), of circle default: 90 deg == left turn
        
        Create arc as polygon of points to facilitate coordinate transformation
        Arc = fraction of a circle with center at self.position, radius of self.radius
        line1: self.position to self.position + r-vector(r, angle=0)
        line2: self.position to self.position + r-vector(r, angle= arc)

        """
        super().__init__(track, road_type=RoadType.TURN, **kwargs)
        tag = self.tag
        tag += "_turn"
        road_width = self.get_road_width()
        if radius is None:
            radius = self.width
        if radius is None:
            radius = road_width
        self.radius = radius
        pos = self.position
        self.arc = arc
        if arc >= 0:
            arc_cent = pos
        else:
            arc_cent = Pt(pos.x+radius, pos.y)
        turn = BlockArc(container=self.container,
                            tag=tag,
                            rotation=self.rotation-90,
                            center=arc_cent,
                            radius=radius,
                            arc=arc,
                            xkwargs={'fill' : 'black'})
        self.comps.append(turn)



    def get_top_left(self):
        """ Get top left corner 
        """
        if self.arc >= 0:
            tlc = Pt(0,0)
        else:
            tlc = Pt(1,0)
        return tlc
