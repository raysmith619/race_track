# car_simple.py        
"""
Simplest of cars
"""
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from car_block import CarBlock,CarType
from block_polygon import BlockPolygon
from block_arc import BlockArc
   
class CarSimple(CarBlock):
    """
    A Strait Part of a road 
    which can be used to construct a road layout
    """
    
            
    def __init__(self,
                 track,
                **kwargs):
        """ Setup Road object
         """
        super().__init__(track, car_type=CarType.SIMPLE, **kwargs)
        if self.width is None:
            self.width = self.get_car_width()
        if self.height is None:
            self.height = self.get_car_length()
        base_color = self.base_color
        if base_color is None:
            base_color = "violet"
        car_base = BlockPolygon(container=self,
                            tag=self.tag,
                            position=Pt(0,0),
                            points=[Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)],
                            xkwargs={'fill' : base_color})
        self.comps.append(car_base)
        
        top_left = .01
        top_right = 1-top_left
        top_back = .25
        top_front = .50
        top_pts = [Pt(top_left,top_back),
                   Pt(top_left, top_front),
                   Pt(top_right, top_front),
                   Pt(top_right, top_back)]
        car_top = BlockPolygon(container=self,
                            tag=self.tag,
                            position=Pt(0,0),
                            points=top_pts,
                            xkwargs={'fill' : 'gray'})
        self.comps.append(car_top)

        windshield_left = top_left
        windshield_right = top_right
        windshield_back = top_front
        windshield_front = windshield_back + .1        
        windshield_pts = [Pt(windshield_left,windshield_back),
                   Pt(windshield_left, windshield_front),
                   Pt(windshield_right, windshield_front),
                   Pt(windshield_right, windshield_back)]
        car_windshield = BlockPolygon(container=self,
                            tag=self.tag,
                            position=Pt(0,0),
                            points=windshield_pts,
                            xkwargs={'fill' : 'lightgray'})
        self.comps.append(car_windshield)

        front_driver_light_pt = Pt(0,1)
        front_pass_light_pt = Pt(1,1)
        '''TBD:front_driver_light = BlockArc(container=car_base,
                        position=car_base.get_relative_point(front_driver_light_pt),
                        start=0, arc=180,
                        radius=.03
                        )
        self.comps.append(front_driver_light)
        '''
    def display(self):
        """ Display thing as a list of components
        """
        super().display()
