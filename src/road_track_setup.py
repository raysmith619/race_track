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
    def __init__(self, road_track, ncar=None, display=True):
        """ Create a demonstration track
        :road_track: track object
        :ncar: number of cars in race default: self.ncar
        :dispaly: display when created default: display
        """
        self.road_track = road_track
        if ncar is None:
            ncar = road_track.ncar
        self.ncar = ncar
        race_track = self.get_race_track()
        road_bin = self.get_road_bin()
        car_bin = race_track.get_car_bin()
        
        SlTrace.lg("road_track pts: %s" % self.road_track.get_absolute_points())
        edge_no = 0
        road_rot = 0.               # Going up, for now              
        turn_arc = -90.
        road_width = road_track.get_road_width()
        road_length = road_track.get_road_length()       # height of entry
        pos = Pt(1-2*road_width, 1*road_length)             # Right lower corner with a padding
        
        ###road_rot = 90               # TFD going right to left
        ###pos = Pt(1-2*road_width, 1-road_length)
        nstrait = 7
        abs_pos = self.road_track.get_absolute_point(pos)
        pos_coords = self.road_track.pts2coords(abs_pos)
        SlTrace.lg("Starting pos: %s %s" % (pos, pos_coords))
        start_road = None              # Set to first road of track
        for edge_no in range(1, 5):     # Edges 1 to 4
            for i in range(nstrait):
                if edge_no == 1 and i == 0:                 # Edge 1
                    road = road_bin.get_entry(0)            # Use first entry in road_bin
                    entry = race_track.add_to_track(road,x=pos_coords[0], y=pos_coords[1],
                                                    select=False, display=False)
                    '''
                    entry = RoadStrait(self.road_track,
                                             rotation=road_rot,
                                             position=pos,
                                             origin=origin)
                    '''
                    start_road = entry
                else:
                    entry = entry.front_add_type(new_type=RoadStrait)
                self.add_entry(entry)
                SlTrace.lg("edge_no:%d entry:%d" % (edge_no, i))
                SlTrace.lg("%s rot: %.0f pos: %s %s  front add: rot: %.0f pos: %s" %
                           (entry, entry.get_rotation(), entry.get_position(), entry.get_position_coords(),
                           entry.get_front_addon_rotation(), entry.abs_front_pos()))
            entry = entry.front_add_type(new_type=RoadTurn, modifier="left")
            self.add_entry(entry)
            SlTrace.lg("Edge %d corner %s: pts: %s" %
                    (edge_no, entry.get_tag_list(), entry.get_absolute_points()))

        self.display()
        ncar = self.ncar
        car_idx = 0             # rotate in bin if necessary
        for idx in range(ncar):
            road = start_road
            for _ in range(idx):
                road = road.get_front_road() # get next road for start
            while True:
                car = car_bin.get_entry(car_idx)    # Get next entry in bin
                if car is  None:
                    car_idx = 0
                    continue
                car_idx += 1
                break
            if idx % 2 == 1:
                side_dist = .55
            else:
                side_dist = .05
            car_position = road.get_position_at(side_dist=side_dist)
            car.side_dist = side_dist
            car_abs_position = race_track.get_absolute_point(car_position)
            SlTrace.lg("car[%d] %s pos:%s[%s]" % (idx, car, car_position, car_abs_position))    
            x,y = road.pts2coords(car_abs_position)
            SlTrace.lg("     coords:[%d,%d]" % (x,y))    
            race_track.add_to_track(car,x=x, y=y, rotation=road.get_rotation_at(dist=0),
                                    select=False, display=False)
        self.display()
        race_track.race_setup()
        race_track.race_start()

 
    def display(self):
        self.road_track.display()


    def get_race_track(self):
        road_track = self.road_track
        race_track = road_track.race_track
        return race_track

    def get_road_bin(self):
        race_track = self.get_race_track()
        road_bin = race_track.get_road_bin()
        return road_bin
    
    
    def add_entry(self, entry):
        """ Add next entry
        :entry: completed entry
        """
        self.road_track.add_entry(entry)
        