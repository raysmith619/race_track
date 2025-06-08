# road_bin_setup.py
"""
Set up road bin panel
"""
from homcoord import *
from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock
from road_block import RoadBlock
from road_straight import RoadStraight
from road_turn import RoadTurn
from road_straight import RoadStraight
from road_turn import RoadTurn



class RoadBinSetup:
    def __init__(self, race_track, road_bin):
        """ Setup road bin with choices to add
        :race_track: race track (RaceTrack) reference
        :road_bin: bin of road choices
        """
        self.race_track = race_track
        self.road_bin = road_bin
        
        SlTrace.lg("RoadBinSetup: road_bin pts: %s" % self.road_bin.get_absolute_points())

        road_rot = 90.
        road_rot = 0            # HACK
        nentries = 4            # Number of entries (space)
        entry_space = .08       # between entries
        entry_width = (1.-nentries*entry_space)/nentries
        entry_height = 1.-2*entry_space       # height of entry
        pos_inc = Pt(entry_space+entry_width, 0.)    # to next entry
        pos = Pt(entry_space, entry_space)  # HACK - Add extra  to move to right
        entry = RoadStraight(self.road_bin,
                                 rotation=road_rot,
                                 position=pos,
                                 width=entry_width,
                                 height=entry_height)
        SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
        self.add_entry(entry)
        self.race_track.display()
        
        pos_turn = Pt(pos.x+entry_width+entry_space, entry_space)
        radius_turn = entry_width
        rot_turn = road_rot
        entry_width = .3 #TFD
        turn_box = RoadBlock(self.road_bin,
                            position=pos_turn,
                            height=entry_height,
                            width=entry_width/2,
                            rotation=road_rot)
        
        turn = RoadTurn(turn_box,
                                 radius=1,
                                 arc=-90.,
                                 rotation=rot_turn)
        turn_box.add_components(turn)
        self.add_entry(turn)    # So select won't hickup                                 
        SlTrace.lg("turn pts: %s" % turn_box.get_absolute_points())
        self.add_entry(turn_box)
        self.race_track.display()
        pos += pos_inc


    def add_entry(self, entry, origin="road_bin"):
        """ Add next entry
        :entry: completed entry
        :origin: origin of block, used to id starting point
        """
        entry.origin = origin
        self.road_bin.add_entry(entry, origin=origin)
     