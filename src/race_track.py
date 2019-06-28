# race_track.py        
"""
Basis of a race track
Includes RoadTrack with road and car bins
"""
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from road_track import RoadTrack
from block_panel import BlockPanel
from block_block import BlockBlock,BlockType
from block_polygon import BlockPolygon
from road_block import RoadBlock,SurfaceType
from road_strait import RoadStrait
from road_panel import RoadPanel
   
class RaceTrack(RoadTrack):
    """
    Race track 
    which can be used to construct a track plus road, track bins
    """
            
    def __init__(self,
                bin_thick=50,           # Bin thickness in pixels
                **kwargs
                ):
        """ Setup track plus bin
        if container is None:
            set width, height to pixel(absolute)
        """
        self.car_bin = None             # Set if present
        self.road_bin = None
        self.road_track = None
        
        super().__init__(**kwargs)
        canvas = self.get_canvas()
        if canvas is None:
            self.canvas = Canvas(width=self.cv_width, height=self.cv_height)
        # Calculate bin dimensions, as fractions of canvas
        # Attempt to give fixed bin thickness
        bin_offset = 2.         # Offset from edge
        cv_height = self.get_cv_height()
        cv_width = self.get_cv_width()
        SlTrace.lg("RaceTrack: width=%.1f heitht=%.1f position=%s cv_width=%.1f cv_height=%.1f"
                   % (self.width, self.height, self.position, cv_width, cv_height))
        road_bin_height = bin_thick/cv_height
        offset_y = bin_offset/cv_height
        offset_x = bin_offset/cv_width 
        car_bin_width = bin_thick/cv_width
        car_bin_height = 1. - road_bin_height - offset_y
        road_bin_width = 1. - car_bin_width - offset_x
        track_position = Pt(car_bin_width+offset_x, road_bin_height+offset_y)
        track_width = 1. - car_bin_width - offset_x
        track_height = 1. - road_bin_height - offset_y
        car_bin_position = Pt(offset_x, road_bin_height)
        road_bin_position = Pt(car_bin_width, offset_y)
        SlTrace.lg("car_bin size: width=%.1f(%.1f) height=%.1f( %.1f)" %
                    (self.width2pixel(car_bin_width),car_bin_width, self.height2pixel(car_bin_height), car_bin_height))
        SlTrace.lg("car_bin pos: x=%.1f(%.1f) y=%.1f(%.1f)" %
                    (self.width2pixel(car_bin_position.x),car_bin_position.x, self.height2pixel(car_bin_position.y), car_bin_position.y))
        self.car_bin = BlockPanel(tag="car_bin",
                             container=self, position=car_bin_position,
                             width=car_bin_width, height=car_bin_height,
                             background="lightpink")
         
        self.road_bin = RoadPanel(self, position=road_bin_position,
                             width=road_bin_width, height=road_bin_height,
                             background="lightgray")
        SlTrace.lg("road_bin pts: %s" % self.road_bin.get_absolute_points())
        
        self.road_track = RoadTrack(container=self, position=track_position,
                               width=track_width, height=track_height,
                               background="lightgreen")

    def add_to_road_bin(self, road):
        """ Add road to bin
        :road: road instance
            road.position is based on road bin geometry
            road.container will be set to containing entity
        """
        road.container = self.road_bin
        self.road_bin.add_components(road)


    def get_road_bin(self):
        return self.road_bin


    def get_car_bin(self):
        return self.car_bin


    def get_road_track(self):
        return self.road_track
        
        
    def display(self):
        """ Display track
        """
        super().display()   # Display any basic components
        
                            # Display major components
        if self.car_bin is not None:
            self.car_bin.display()
        if self.road_bin is not None:
            self.road_bin.display()
        if self.road_track is not None:
            self.road_track.display()
        
        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    from road_block import RoadBlock
    from road_turn import RoadTurn
    from block_arc import BlockArc

    SlTrace.setFlags("short_points")
    
    width = 600     # Window width
    height = width  # Window height
    rotation = None # No rotation
    pos_x = None
    pos_y = None
    parser = argparse.ArgumentParser()
    dispall = False      # Display every change
    
    parser.add_argument('--width=', type=int, dest='width', default=width)
    parser.add_argument('--height=', type=int, dest='height', default=height)
    parser.add_argument('--pos_x=', type=float, dest='pos_x', default=pos_x)
    parser.add_argument('--pos_y=', type=float, dest='pos_y', default=pos_y)
    parser.add_argument('--rotation=', type=float, dest='rotation', default=rotation)
    args = parser.parse_args()             # or die "Illegal options"
    
    width = args.width
    height = args.height
    pos_x = args.pos_x
    pos_y = args.pos_y
    rotation = args.rotation
    
    SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
    SlTrace.lg("args: %s\n" % args)
    
            
    frame = Frame(width=width, height=height, bg="", colormap="new")
    frame.pack()
    canvas = Canvas(frame, width=width, height=height)
    canvas.pack()   
    th_width = 1.
    th_height = 1.
    position = None
    if pos_x is not None or pos_y is not None:
        if pos_x is None:
            pos_x = 0.
        if pos_y is None:
            pos_y = 0.
        position = Pt(pos_x, pos_y)
        
    tR = RaceTrack(canvas=canvas, width=th_width, height=th_height,
                   position=position,
                   cv_width=width, cv_height=height,
                   rotation=rotation)
    tR.display()
    
    mainloop()