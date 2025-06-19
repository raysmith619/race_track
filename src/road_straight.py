# road_straight.py        
"""
Straight road segment
"""
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType
from block_polygon import BlockPolygon
from road_block import RoadBlock,RoadType
   
class RoadStraight(RoadBlock):
    """
    A Straight Part of a road 
    which can be used to construct a road layout
    """
    
            
    def __init__(self,
                 track,
                **kwargs):
        """ Setup Road object
         """
        super().__init__(track, road_type=RoadType.STRAIGHT, **kwargs)
        if self.width is None:
            self.width = self.get_road_width()
        if self.height is None:
            self.height = self.get_road_length()
        xkwargs = self.xkwargs
        if xkwargs is None:
            xkwargs = {'fill' : 'black'}
        straight = BlockPolygon(container=self,
                            tag=self.tag,
                            position=Pt(0,0),
                            points=[Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)],
                            xkwargs=xkwargs)
        self.comps.append(straight)
        median_width = self.median_width
        median_x = self.median_x
        off_edge = self.off_edge
        edge_width = self.edge_width
        median_strip = BlockPolygon(container=self,
                            tag=self.tag,
                            position=Pt(0,0),
                            points=[Pt(median_x-median_width, 0),
                                    Pt(median_x-median_width, 1),
                                    Pt(median_x+median_width, 1),
                                    Pt(median_x+median_width, 0)],
                            xkwargs={'fill' : 'yellow', 'width' : 2})
        self.comps.append(median_strip)
        left_edge = BlockPolygon(container=self,
                            tag=self.tag,
                            position=Pt(0,0),
                            points=[Pt(off_edge, 0),
                                    Pt(off_edge, 1),
                                    Pt(off_edge+edge_width, 1),
                                    Pt(off_edge+edge_width, 0)],
                            xkwargs={'fill' : 'white', 'width' : 2})
        self.comps.append(left_edge)
        right_edge = BlockPolygon(container=self,
                            tag=self.tag,
                            position=Pt(0,0),
                            points=[Pt(1-off_edge, 0),
                                    Pt(1-off_edge, 1),
                                    Pt(1-off_edge-edge_width, 1),
                                    Pt(1-off_edge-edge_width, 0)],
                            xkwargs={'fill' : 'white', 'width' : 2})
        self.comps.append(right_edge)


    def __repr__(self):
        return self.__str__()


    def __str__(self):
        str_str = self.__class__.__name__ + " id:%s" % self.id
        if hasattr(self, "front_road") and self.front_road is not None:
            str_str += f" front_road:{self.front_road.id}"
        if hasattr(self, "arc") and self.arc is not None:
            str_str += " arc:%.0f" % self.arc
        if hasattr(self, "origin") and self.origin is not None:
            str_str += " in:%s" % self.origin
        if hasattr(self, "state") and self.state is not None:
            str_str += " state:%s" % self.state
        return str_str

        
    def display(self):
        """ Display thing as a list of components
        """
        super().display()
