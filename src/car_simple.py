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

        head_light_color = "yellow"
        hl_hight = .06
        hl_width = 4*hl_hight
        hl_inset = hl_width*.1
        hl_fw_pt = Pt(0,hl_hight)
        hl_rw_pt = Pt(hl_width,0)
        fd_light_pt = Pt(hl_inset,1-hl_hight)
        fd_light_pts = [fd_light_pt, fd_light_pt+hl_fw_pt,
                        fd_light_pt+hl_fw_pt+hl_rw_pt,
                        fd_light_pt+hl_rw_pt]

        front_driver_light = BlockPolygon(container=self,
                        color=head_light_color,
                        points=fd_light_pts
                        )
        self.comps.append(front_driver_light)
        fp_light_pt = Pt(1-hl_width-hl_inset,1-hl_hight)
        fp_light_pts = [fp_light_pt, fp_light_pt+hl_fw_pt,
                        fp_light_pt+hl_fw_pt+hl_rw_pt,
                        fp_light_pt+hl_rw_pt]

        front_pass_light = BlockPolygon(container=self,
                        color=head_light_color,
                        points=fp_light_pts
                        )
        self.comps.append(front_pass_light)

        rear_light_color = "red"
        rl_radius = .05
        rl_dia = 2*rl_radius
        rl_inset = rl_dia*.1
        rl_fw_pt = Pt(0,rl_radius)
        rl_rw_pt = Pt(rl_dia,0)
        rd_light_pt = Pt(rl_inset, 0)
        rd_light_pts = [rd_light_pt, rd_light_pt+rl_fw_pt,
                        rd_light_pt+rl_fw_pt+rl_rw_pt,
                        rd_light_pt+rl_rw_pt]

        rear_driver_light = BlockPolygon(container=self,
                        color=rear_light_color,
                        points=rd_light_pts
                        )
        self.comps.append(rear_driver_light)
        
        rp_light_pt = Pt(1-rl_dia-rl_inset, 0)
        rp_light_pts = [rp_light_pt, rp_light_pt+rl_fw_pt,
                        rp_light_pt+rl_fw_pt+rl_rw_pt,
                        rp_light_pt+rl_rw_pt]

        rear_pass_light = BlockPolygon(container=self,
                        color=rear_light_color,
                        points=rp_light_pts
                        )
        self.comps.append(rear_pass_light)

    
    def display(self):
        """ Display thing as a list of components
        """
        super().display()
