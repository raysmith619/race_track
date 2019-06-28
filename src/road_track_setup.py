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
        road_width = road_track.get_road_width()
        road_length = road_track.get_road_length()       # height of entry
        pos_inc = Pt(0, road_length)    # to next entry
        pos = Pt(.5, .5)
        nstrait = 4
        for i in range(nstrait):                # Edge 1
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,
                                     width=road_width,
                                     height=road_length)
            SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
            self.add_entry(entry)
            pos = entry.get_top_left()

        pos = entry.get_relative_point(Pt(0,0))
        turn_fudge = Pt(-road_width/11, road_length/6)
        pos = entry.get_top_left()+turn_fudge
        corner = RoadTurn(self.road_track,
                                 arc=90.,
                                 rotation=road_rot,
                                 position=pos)
        SlTrace.lg("entry pts: %s" % corner.get_absolute_points())
        self.add_entry(corner)
        pos += pos_inc
        
        road_rot += 90.
        pos = entry.get_relative_point(Pt(0+.285,1.034))
        for i in range(nstrait):                    # Edge 2
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,
                                     width=road_width,
                                     height=road_length)
            SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
            self.add_entry(entry)
            pos = entry.get_top_left()
        pos = entry.get_relative_point(Pt(-.05,2.35))
        corner = RoadTurn(self.road_track,
                                 arc=90.,
                                 rotation=road_rot,
                                 position=pos)
        SlTrace.lg("entry pts: %s" % corner.get_absolute_points())
        self.add_entry(corner)
        pos += pos_inc

        road_rot += 90
        pos = entry.get_relative_point(.15,2.05)         # left lower to left
        for i in range(nstrait):                        # Edge 3
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,
                                     width=road_width,
                                     height=road_length)
            SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
            self.add_entry(entry)
            pos = entry.get_top_left()

        pos = entry.get_relative_point(Pt(-.055, 1.15))
        corner = RoadTurn(self.road_track,
                                 arc=90.,
                                 rotation=road_rot,
                                 position=pos)
        SlTrace.lg("entry pts: %s" % corner.get_absolute_points())
        self.add_entry(corner)

        road_rot += 90
        pos = entry.get_relative_point(.34, 1)
        for i in range(nstrait):                    # Edge 4
            entry = RoadStrait(self.road_track,
                                     rotation=road_rot,
                                     position=pos,
                                     width=road_width,
                                     height=road_length)
            SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
            self.add_entry(entry)
            pos = entry.get_top_left()
 
        pos = entry.get_relative_point(Pt(-.045,2.37))
        corner = RoadTurn(self.road_track,
                                 arc=90.,
                                 rotation=road_rot,
                                 position=pos)
        SlTrace.lg("entry pts: %s" % corner.get_absolute_points())
        self.add_entry(corner)
       
        
        if display:
            self.road_track.display()
            

    def add_entry(self, entry):
        """ Add next entry
        :entry: completed entry
        """
        self.road_track.comps.append(entry)
        