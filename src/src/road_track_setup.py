# road_track_setup.py
"""
Set up road bin panel
"""
from homcoord import *
from select_trace import SlTrace
from select_error import SelectError


from road_strait import RoadStrait
from road_turn import RoadTurn
from road_strait import RoadStrait
from road_turn import RoadTurn



class RoadTrackSetup:
    def __init__(self, road_track, display=True):
        """ Create a demonstration track
        :road_track: track object
        :dispaly: display when created default: display
        """
        self.road_track = road_track
        
        SlTrace.lg("road_track pts: %s" % self.road_track.get_absolute_points())

        road_rot = 0.
        turn_arc = -90.
        road_width = road_track.get_road_width()
        road_length = road_track.get_road_length()       # height of entry
        pos_inc = Pt(0, road_length)    # to next entry
        pos = Pt(1-2*road_width, 2*road_length)             # Right lower corner with a padding
        nstrait = 8
        origin = "road_track"
        for i in range(nstrait):                # Edge 1
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,
                                     origin=origin)
            self.add_road(entry)
            SlTrace.lg("Edge 1 entry(%d) %s: pts: %s" % (i, entry.get_tag_list(), entry.get_absolute_points()))
            pos = entry.get_top_left()
            SlTrace.lg("Edge 1 pos(%d) %s: pts: %s" % (i, entry.get_tag_list(), self.road_track.get_absolute_point(pos)))

        corner = RoadTurn(self.road_track,
                                 arc=turn_arc,
                                 rotation=road_rot,
                                 position=pos,
                                 origin=origin)
        SlTrace.lg("Edge 1 corner %s: pts: %s" % (corner.get_tag_list(), corner.get_absolute_points()))
        self.add_road(corner)
         
        road_rot += 90.
        pos = entry.get_top_left()
        for i in range(nstrait):                    # Edge 2
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,origin=origin)
            self.add_road(entry)
            SlTrace.lg("Edge 2 entry(%d) %s: pts: %s" % (i, entry.get_tag_list(), entry.get_absolute_points()))
            pos = entry.get_top_left()
            SlTrace.lg("Edge 2 pos(%d) %s: pts: %s" % (i, entry.get_tag_list(), self.road_track.get_absolute_point(pos)))
        corner = RoadTurn(self.road_track,
                                 arc=turn_arc,
                                 rotation=road_rot,
                                 position=pos,origin=origin)
        SlTrace.lg("Edge 2 corner pts: %s" % corner.get_absolute_points())
        self.add_road(corner)
        self.display()
        
        pos += pos_inc

        road_rot += 90
        pos = entry.get_top_left()         # left lower to left
        for i in range(nstrait):                        # Edge 3
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,origin=origin)
            SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
            self.add_road(entry)
            pos = entry.get_top_left()

        corner = RoadTurn(self.road_track,
                                 arc=turn_arc,
                                 rotation=road_rot,
                                 position=pos,origin=origin)
        SlTrace.lg("entry pts: %s" % corner.get_absolute_points())
        self.add_road(corner)

        road_rot += 90
        pos = entry.get_top_left()
        for i in range(nstrait):                    # Edge 4
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,origin=origin)
            SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
            self.add_road(entry)
            pos = entry.get_top_left()
 
        corner = RoadTurn(self.road_track,
                                 arc=turn_arc,
                                 rotation=road_rot,
                                 position=pos,origin=origin)
        SlTrace.lg("entry pts: %s" % corner.get_absolute_points())
        self.add_road(corner)
       
        
        if display:
            self.display()
            
 
    def display(self):
        self.road_track.display()
        

    def add_road(self, entry):
        """ Add next entry
        :entry: completed entry
        """
        self.road_track.add_road(entry)
        