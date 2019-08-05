# car_block.py        
"""
Simple abstract car
Uses BlockBlock parts
"""
from enum import Enum
import copy
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock, BlockType

class CarType(Enum):
    COMPOSITE = 1
    SIMPLE = 2
    TRUCK = 3
    RACECAR = 4


   
class CarBlock(BlockBlock):
    """
    A basis for all cars 
    which can be used to construct a car
    """
    
            
    def __init__(self,
                container,
                car_type=CarType.COMPOSITE,
                car_width=None,
                car_length=None,
                base_color=None,
                side_dist=.05,
                **kwargs):
        """ Setup Road object
        :container: Road object containing this object
                      OR
                    RoadTrack 
        :road_width:  road's width as fraction of width
                        default: track's road_width
        :road_length:  road's length as fraction of width
                        default: track's road_length
        :base_color: car's base color default: CHOSEN
        :side_dist: distance, as a fraction of road width, from the left side of the road
        """
        SlTrace.lg("\nCarBlock: %s %s container: %s" % (car_type, self, container))    
        super().__init__(container=container, **kwargs)
        self.side_dist = side_dist
        self.base_color = base_color        
        self.car_width = car_width
        self.car_length = car_length


    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = super().__deepcopy__(memo)
        new_inst.car_width = self.car_width
        new_inst.car_length = self.car_length
        new_inst.base_color = self.base_color
        new_inst.side_dist = self.side_dist
                
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
    

    def get_car_width(self):
        """ Get car width in fraction of container
        """
        if self.car_width is None:
            return self.container.get_car_width()
        
        return self.car_width
        

    def get_car_length(self):
        """ Get car length in fraction of container
        """
        if self.car_length is None:
            return self.container.get_car_length()
        
        return self.car_length
        

    def get_road_rotation(self):
        """ Get road rotation in degrees
        Adds in  container or track rotation if any
        :returns: None if no rotation
        """
        if self.container is not None:
            rot = self.container.get_car_rotation()
            rot2 = self.rotation
            if rot2 is None:
                rot2 = rot
            return rot2
        
        rot = self.track.get_car_rotation()
        rot2 = self.rotation
        if rot2 is None:
            rot2 = rot
        return rot2


    def get_minimum_speed(self):
        """ Minimum driving speed for car
        in mph
        """
        return self.get_road_track().get_minimum_speed()


    def get_maximum_speed(self):
        """ Maximum driving speed for car
        in mph
        """
        return self.get_road_track().get_maximum_speed()


    def get_turn_speed(self):
        """ Maximum driving speed for car
        in mph
        """
        return self.get_road_track().get_turn_speed()


    def get_acc_speed(self, delta_time=1.):
        """ Max acceleration per second for car
        in mph/sec e.g. 0 to 60 in 4 seconds == 15 gross approximation!
        """
        acc_per_sec = 10
        return acc_per_sec * delta_time
    