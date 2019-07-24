# car_bin_setup.py
"""
Set up car bin panel
"""
from homcoord import *
from select_trace import SlTrace
from select_error import SelectError


from car_simple import CarSimple



class CarBinSetup:
    def __init__(self, car_bin):
        self.car_bin = car_bin
        
        SlTrace.lg("CarBinSetup: car_bin pts: %s" % self.car_bin.get_absolute_points())

        car_rot = 0            # HACK
        nentries = 4            # Number of entries (space)
        entry_space = .08       # between entries
        entry_width = 5*(1.-nentries*entry_space)/nentries
        entry_height = .25*(1.-2*entry_space)       # height of entry
        pos_inc = Pt(0., 1.2*entry_height)    # to next entry
        pos = Pt(entry_space, entry_space)  # HACK - Add extra  to move to right
        
        entry = CarSimple(self.car_bin,
                                 rotation=car_rot,
                                 position=pos,
                                 width=entry_width,
                                 height=entry_height,
                                 base_color="red")
        SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
        self.add_entry(entry)

        pos += pos_inc
        entry = CarSimple(self.car_bin,
                                 rotation=car_rot,
                                 position=pos,
                                 width=entry_width,
                                 height=entry_height,
                                 base_color="blue")
        SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
        self.add_entry(entry)
        
        pos += pos_inc
        entry = CarSimple(self.car_bin,
                                 rotation=car_rot,
                                 position=pos,
                                 width=entry_width,
                                 height=entry_height,
                                 base_color="green")        
        SlTrace.lg("entry pts: %s" % entry.get_absolute_points())
        self.add_entry(entry)


    def add_entry(self, entry, origin="car_bin"):
        """ Add next entry
        :entry: completed entry
        :origin: origin of block, used to id starting point
        """
        entry.origin = origin
        self.car_bin.add_entry(entry)
     