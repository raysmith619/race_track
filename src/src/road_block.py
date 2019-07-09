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
        self.road_width = road_width 
        self.road_length = road_length
        if surface is None and container is not None:
            surface = container.surface
        self.surface = surface
        super().__init__(container=container, **kwargs)        



    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = super().__deepcopy__(memo)
        new_inst.road_width = self.road_width
        new_inst.road_length = self.road_length
        new_inst.surface = self.surface
                
        return new_inst
        
        
    
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
        if not self.visible:
            return              # Skip if invisible
        
        SlTrace.lg("display %s: %s" % (self.get_tag_list(), self), "display")
        for comp in self.comps:
            comp.display()
        self.task_update()


    def get_road_track(self):
        top = self.get_top_container()
        return top
    

    def get_road_width(self):
        """ Get road width in fraction of container
        """
        if self.road_width is None:
            return self.container.get_road_width()
        
        return self.road_width
        

    def get_road_length(self):
        """ Get road length in fraction of container
        """
        if self.road_length is None:
            return self.container.get_road_length()
        
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


    def get_road_surface(self):
        return self.track.get_road_surface()
    