# road_strait.py        
"""
Strait road segment
"""
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock,BlockType
from block_polygon import BlockPolygon
from road_block import RoadBlock,RoadType
   
class RoadStrait(RoadBlock):
    """
    A Strait Part of a road 
    which can be used to construct a road layout
    """
    
            
    def __init__(self,
                 track,
                **kwargs):
        """ Setup Road object
         """
        super().__init__(track, road_type=RoadType.STRAIT, **kwargs)
        if self.width is None:
            self.width = self.road_width
        if self.height is None:
            self.height = self.road_width
        strait = BlockPolygon(container=self.container,
                            tag=self.tag,
                            position=self.position,
                            width=self.width,
                            height=self.height,
                            rotation=self.rotation,
                            ctype=BlockType.POLYGON,
                            points=[Pt(0,0), Pt(1,0), Pt(1,1), Pt(0,1)],
                            xkwargs={'fill' : 'black'})
        self.comps.append(strait)

    
    def display(self):
        """ Display thing as a list of components
        """
        super().display()
