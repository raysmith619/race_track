# road_block.py        
"""
Basis of a road network
Uses BlockBlock parts
"""
from enum import Enum
import copy
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock, BlockType
from wx.lib.gizmos.dynamicsash import DS_DRAG_CORNER

class RoadType(Enum):
    COMPOSITE = 1
    STRAIT = 2
    TURN = 3
    CROSS = 4

class SurfaceType(Enum):
    DEFAULT = 1
    ASFAULT = 2
    CONCRETE = 3
    DIRT = 4
    GRASS = 5


   
class RoadBlock(BlockBlock):
    """
    A Part of a road 
    which can be used to construct a road layout
    """
    
            
    def __init__(self,
                container,
                road_type=RoadType.COMPOSITE,
                road_width=None,
                road_length=None,
                surface=None,
                **kwargs):
        """ Setup Road object
        :container: Road object containing this object
                      OR
                    RoadTrack 
        :road_type: container type defalut:COMPOSITE
        :road_width:  road's width as fraction of width
                        default: track's road_width
        :road_length:  road's length as fraction of width
                        default: track's road_length
        """
        SlTrace.lg("\nRoadBlock: %s %s container: %s" % (road_type, self, container))    
        self.road_type = road_type
        if road_width is None and container is not None:
            road_width = container.road_width
        self.road_width = road_width
        if road_length is None and container is not None:
            road_length = container.road_length
        self.road_length = road_length
        if surface is None and container is not None:
            surface = container.surface
        self.surface = surface
        super().__init__(container=container, **kwargs)        
        
        
    
    def add_components(self, comps):
        """ Add component/list of components
        :comps: one or list of components
        """
        if not isinstance(comps, list):
            comps = [comps]
        for comp in comps:
            self.comps.append(comp)

    
    def display(self):
        """ Display thing as a list of components
        """
        canvas = self.get_canvas()
        canvas.update_idletasks()
        canvas.update()
        if not self.visible:
            return              # Skip if invisible
        
        SlTrace.lg("display %s: %s" % (self.get_tag_list(), self))
        for comp in self.comps:
            comp.display()
        

    def get_road_width(self):
        """ Get road width in fraction of container
        """
        return self.road_width
        

    def get_road_length(self):
        """ Get road length in pixels
        """
        return self.road_length
        

    def get_road_rotation(self):
        """ Get road rotation in degrees
        Adds in  container or track rotation if any
        :returns: None if no rotation
        """
        if self.container is not None:
            rot = self.container.get_road_rotation()
            rot2 = self.rotation
            if rot2 is None:
                rot2 = rot
            return rot2
        
        rot = self.track.get_road_rotation()
        rot2 = self.rotation
        if rot2 is None:
            rot2 = rot
        return rot2




    def get_relative_point(self, *ptxy):
        """ get single point relative to current position
        :ptxy: current relative point or xy
        :returns: point in container's reference
        """
        if len(ptxy)== 1 and isinstance(ptxy[0], Pt):
            pt = ptxy[0]
        else:
            pt = Pt(ptxy[0], ptxy[1])
        pts = self.get_relative_points(pt)
        return pts[0]


    def get_relative_points(self, points=None):
        """ Get points based on current block position
        :points: base point/points to translate
                defajlt: self.points
        :returns: list of translated points
                e.g. if default gives points as transformed
                by base transform
        """
        comp = self.comps[0]
        return comp.get_relative_points(points)


    def get_road_surface(self):
        return self.track.get_road_surface()


    def get_top_left(self):
        """ Get top left corner 
        """
        tlc = self.get_relative_point(Pt(0,1))
        return tlc


    def get_top_right(self):
        """ Get top left corner 
        """
        trc = self.get_relative_point(Pt(1,1))
        return trc
    