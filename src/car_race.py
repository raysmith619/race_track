#car_race.py
"""
Contain, track, and control race operation
"""
import time
import random

from homcoord import *

from select_trace import SlTrace
from select_error import SelectError

from road_turn import RoadTurn
from road_strait import RoadStrait

class CarInfo:
    """
    Car startup info
    """
    def __init__(self, car, road_start):
        """ Car startup info
        :car: 
        :road: in which the car starts
        """
        self.car = car
        self.road_start = road_start
        self.road_cur = self.road_start
        self.road_prev = self.road_start           # Previous road so we can check for changes
        self.start_dist = 0.            # point in circuit
        self.distance = 0.              # Miles
        self.side_dist = 0.             # Distance (fraction of width from left side of road)
        self.speed = 0.                 # mph
                      

class CircuitSegmentInfo:
    """ Info for each segment to facilitate car placement
    """
    def __init__(self, road=None, start_dist=0., end_dist=0.):
        """ Setup circuit segment info 
        :road: component road
        :start_dist: starting distance
        :end_dist: ending distance
        """        
        self.road = road
        self.start_dist=start_dist
        self.end_dist=end_dist
        
class CarRace:
    """
    Car race info - used to control race
    """
    def __init__(self, race_track, road_list=None, car_infos=None):
        """
        :race_track: connection to race track information and control
        :cars:  dictionary (by block id) of cars in race
        :road_list: list of roads from start through end of circuit
        :car_infos: dictionary of car starting info(CarStart)
        :update_interval: race update interval in seconds
        """
        self.race_track = race_track
        if road_list is None:
            road_list = []
        self.road_list = road_list
        if car_infos is None:
            car_infos = {}
        self.car_infos = car_infos
        self.car_states = {}                            # using CarInfo class but for current race info
        self.segment_infos = []
        self.prev_time = self.time = time.clock()
        self.circuit_dist = 1            # Circut distance in top level
        self.running = False
        self.pausing = False
        
        
    def add_car_info(self, car, road):
        """ Setup car startup info
        :car: car to add
        :road: car starting road
        """
        car_info = CarInfo(car, road)
        self.car_infos[car.id] = car_info
        return car_info


        

    def get_road_width(self):
        """ Get road width in with respect to container
        """
        race_track = self.get_race_track()
        return race_track.get_road_width()


    def mile2scf(self, dist_mile):
        """ Convert miles to screen fraction (i.e. position units
        Assumes road width (state 2 lane of 45 feet)
        """
        race_track = self.get_race_track()
        road_width_feet = race_track.get_road_width_feet()
        scf = dist_mile*5280. * road_width_feet/45. * race_track.get_road_width()
        return scf 


    def setup_car_info(self, car_info):
        car = car_info.car
        car.clear_selected()
        for segment_info in self.segment_infos:
            road = segment_info.road
            if car_info.road_start.id == road.id:
                car_info.start_dist = segment_info.start_dist
                break

    def setup(self):
        """ Setup race with any optimizations required
        :returns: True iff successful in setting up race
        """
        dist = 0        # cumulative distance around circuit
        for road in self.road_list:
            length_dist = road.get_length_dist()
            end_dist = dist + length_dist   # use and remember last one
            segment_info = CircuitSegmentInfo(road, start_dist=dist, end_dist=end_dist)
            self.segment_infos.append(segment_info)
            dist = end_dist
            segment_info = CircuitSegmentInfo(road)
        self.circuit_dist = end_dist     # Full lap
        for car_info in self.car_infos.values():
            self.setup_car_info(car_info)        # complete info, e.g. start_dist
        self.car_states = {}    
        for car_info_id in self.car_infos.keys():
            self.car_states[car_info_id] = self.car_infos[car_info_id]  # set/reset to initial values   
        return True


    def shutdown(self):
        """ Shutdown race, releasing resources
        """
        for car_id in list(self.car_infos.keys()):
            car_info = self.car_infos[car_id]
            car = car_info.car
            car.remove_display_objects()
            if car_id in self.car_states:
                del self.car_states[car_id]
            if car_id in self.car_infos:
                del self.car_infos[car_id]
            
        ''' Leave roads alone
        for road in self.road_list:
            road.remove_display_objects()
        self.road_list = []
        '''
            
    def start(self):
        """ Start race
        """
        self.prev_time = self.time = time.clock()
        self.running = True
        self.pausing = False
        self.update()               # Start first action immediately          

    def pause(self):
        """ Start race
        """
        self.running = False
        self.pausing = True
        self.update()               # Update to new condition          

    def race_continue(self):
        """ Continue race
        """
        self.prev_time = self.time = time.clock()
        self.running = True
        self.pausing = False
        self.update()               # Start first action immediately          

    def stop(self):
        """ Start race
        """
        self.running = False
        self.pausing = False
        self.update()
         
    def update(self):
        """ race update function - called periodically to up state/display
        """
        self.time = time.clock()
        self.delta_time = self.time - self.prev_time
        self.prev_time = self.time
        for car_id in list(self.car_states):
            car_state = self.car_states[car_id]
            self.update_car(car_state, delta_time=self.delta_time)
        if self.running:
            interval_msec = int(self.get_update_interval()*1000)
            self.race_track.mw.after(interval_msec, self.update)
        
        
        
    def update_car(self, car_state, delta_time):
        """ Update car state inrace
        Update car state based on current/previous state
        and delta_time.
        
        :car_state: current car state (CarInfo)
        :delta_time: time since last race update
        """
        if not self.running:
            return                  # No action if not running
        
        
        car = car_state.car
        cur_speed = car_state.speed
        new_distance = car_state.distance + cur_speed*delta_time/3600.
        new_distance_feet = new_distance*5280
        car_state.distance = new_distance
        road_prev = car_state.road_cur
        
        # Update states based on new conditions
        road, in_road_dist = self.get_road_section(car_state)
        road_cur = road
        if issubclass(type(road), RoadTurn):
            if car_state.speed > car.get_turn_speed():
                car_state.speed = (car.get_turn_speed()+car_state.speed)/2
        elif issubclass(type(road), RoadStrait):
            if issubclass(type(road_prev), RoadTurn):
                car_state.speed += random.randint(0,3)*car.get_acc_speed(delta_time)  # random burst
            car_state.speed += car.get_acc_speed(delta_time)
        if car_state.speed > car.get_maximum_speed():
            car_state.speed = (car.get_maximum_speed()+car_state.speed)/2
        if car_state.speed < car.get_minimum_speed():
            car_state.speed = car.get_minimum_speed()

        car_position = road.get_position_at(dist=in_road_dist, side_dist=car.side_dist)        
        car.set_position(position=car_position)
        car_rotation = road.get_rotation_at(dist=in_road_dist)
        car.set_rotation(rotation=car_rotation)
        if SlTrace.trace("car_update"):
            SlTrace.lg("car: %s position: %s rotation: %.0f" % (car, car_position, car_rotation))
        car.display()
        car_state.road_prev = car_state.road_cur
        car_state.road_cur = road_cur
        
    def get_update_interval(self):
        """ update interval in seconds
        """
        return self.race_track.get_update_interval()

    def display(self):
        self.race_track.display()
        
        
    def get_race_track(self):
        """ Get our race track
        """
        return self.race_track
        
        
    def get_road_section(self, car_state):
        """ Get road(section), distance in road section), given car_state
        :car_state:  car state (CarInfo)
        :returns: pair: road, distance screen Fraction
        """
        car_distance = car_state.distance
        car_start_dist = car_state.start_dist
        car_dist_net = self.mile2scf(car_distance)      # Convert to screen fraction (1. is full screen)
        car_circuit_dist = (car_dist_net + car_start_dist) % self.circuit_dist   # Where in circuit
        for segment_info in self.segment_infos:
            if (car_circuit_dist >= segment_info.start_dist
                    and car_circuit_dist <= segment_info.end_dist):
                return segment_info.road, car_circuit_dist-segment_info.start_dist
            
        raise SelectError("get_road_section outside race track")
                