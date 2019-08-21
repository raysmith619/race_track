# road_bin_setup.py
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



class RoadBinSetup:
    def __init__(self, road_bin):
        """ Setup road bin with choices to add
        """
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
        entry = RoadStrait(self.road_bin,
                                 rotation=road_rot,
                                 position=pos,
                                 width=entry_width,
                                 height=entry_height)
        SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
        self.add_entry(entry)
        
        pos_turn = Pt(pos.x+entry_width+entry_space, entry_space)
        radius_turn = entry_width
        rot_turn = road_rot
        entry = RoadTurn(self.road_bin,
                                 arc=-90.,
                                 rotation=rot_turn,
                                 position=pos_turn,
                                 width=entry_width/2,
                                 height=entry_height)
                                 
        SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
        self.add_entry(entry)
        pos += pos_inc


    def add_entry(self, entry, origin="road_bin"):
        """ Add next entry
        :entry: completed entry
        :origin: origin of block, used to id starting point
        """
        entry.origin = origin
        self.road_bin.add_entry(entry, origin=origin)
     