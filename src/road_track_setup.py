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
        edge_no = 0
        road_rot = 0.               # Going up, for now              
        turn_arc = -90.
        road_width = road_track.get_road_width()
        road_length = road_track.get_road_length()       # height of entry
        pos = Pt(1-2*road_width, 2*road_length)             # Right lower corner with a padding
        
        ###road_rot = 90               # TFD going right to left
        ###pos = Pt(1-2*road_width, 1-road_length)
        nstrait = 7
        origin = "road_track"
        abs_pos = self.road_track.get_absolute_point(pos)
        SlTrace.lg("Starting pos: %s %s" % (pos, self.road_track.pts2coords(abs_pos)))
        for edge_no in range(1, 5):     # Edges 1 to 4
            for i in range(nstrait):
                if edge_no == 1 and i == 0:                # Edge 1
                    entry = RoadStrait(self.road_track,
                                             rotation=road_rot,
                                             position=pos,
                                             origin=origin)
                    entry.move_to(position=pos)  #TFD
                else:
                    entry = entry.front_add_type(new_type=RoadStrait)
                self.add_road(entry)
                self.display()
                SlTrace.lg("edge_no:%d entry:%d" % (edge_no, i))
                SlTrace.lg("%s rot: %.0f pos: %s %s  front add: rot: %.0f pos: %s" %
                           (entry, entry.get_rotation(), entry.get_position(), entry.abs_pos(),
                           entry.get_front_addon_rotation(), entry.abs_front_pos()))
            entry = entry.front_add_type(new_type=RoadTurn, modifier="left")
            self.add_road(entry)
            self.display()
            SlTrace.lg("Edge %d corner %s: pts: %s" %
                    (edge_no, entry.get_tag_list(), entry.get_absolute_points()))
 
    def display(self):
        self.road_track.display()
        

    def add_road(self, entry):
        """ Add next entry
        :entry: completed entry
        """
        self.road_track.add_road(entry)
        