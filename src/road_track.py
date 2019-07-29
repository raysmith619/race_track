# road_track.py        
"""
Basis of a road network
Uses RoadBlock parts
"""
from enum import Enum
import copy
from homcoord import *
from tkinter import *

from select_trace import SlTrace
from select_error import SelectError

from block_panel import BlockPanel
from block_block import BlockBlock,BlockType
from block_polygon import BlockPolygon
from block_text import BlockText
from block_check import BlockCheck
from road_block import RoadBlock,SurfaceType
from road_strait import RoadStrait
from car_block import CarBlock

   
class RoadTrack(BlockPanel):
    """
    Road track 
    which can be used to construct a road layout
    Object properties are expressed in relation to the containing object.
    """
    
            
    def __init__(self,
                road_width=.05,
                road_width_feet=45.,
                road_length=.05*2,
                minimum_speed=5.,
                maximum_speed=100,
                ncar=2,
                update_interval=.01,
                turn_speed=5.,
                car_width=None,
                car_length=None,
                surface=SurfaceType.DEFAULT,
                **kwargs
                ):
        """ Setup object
        :car_width: car width as a fraction of track's width dimensions
                default: road_width/2.5
        :car_length: car width as a fraction of track's width dimensions
                default: car_width * 2.5
        :road_width: road width as a fraction of track's width dimensions'
                e.g. 1,1 with container==None ==> block is whole canvas
        :road_length: road width as a fraction of track's width dimensions'
                e.g. 1,1 with container==None ==> block is whole canvas
        :surface: road surface type - determines look and operation/handeling
        :ncar: default number of cars in race
        NOTE: container is race_track                                                    collisions)
        """
        SlTrace.lg("RoadTrack: %s" % (self))
        if car_width is None:
            car_width = road_width/2.5
        self.car_width = car_width
        if car_length is None:
            car_length = car_width*2.5
        self.car_length = car_length
        super().__init__(**kwargs)
        if self.container is None:
            canvas = self.get_canvas()
            if canvas is None:
                self.canvas = Canvas(width=self.cv_width, height=self.cv_height)
        self.minimum_speed = minimum_speed
        self.maximum_speed = maximum_speed
        self.ncar = ncar
        self.turn_speed = turn_speed
        self.update_interval = update_interval
        self.race_track = self.container
        self.roads = {}     # road sections of the track by block id
        self.cars = {}      # cars in track by block id
        self.road_width = road_width
        self.road_length = road_length
        self.surface = surface
        self.background = "lightgreen"
        self.road_width_feet = road_width_feet

    def add_entry(self, entries, origin="road_track"):
        """ Add next entry
        :entries: single or list of entities (cars,roads) 
        :origin: origin of block, if not already specified in entry starting point
        """
        if not isinstance(entries, list):
            entries = [entries]
        
        for entry in entries:
            if entry.origin is None:
                entry.origion = origin
            if issubclass(type(entry), RoadBlock):
                self.roads[entry.id] = entry
            else:
                self.cars[entry.id] = entry
            self.id_blocks[entry.id] = entry


    def remove_entry(self, entries_ids):
        """ Remove entry(s) from track
        :entries_ids: entries/ids
        """
        if not isinstance(entries_ids, list):
            entries_ids = [entries_ids]     # list of one
        for entry_id in entries_ids:
            if isinstance(entry_id, int):
                entry = self.id_blocks[entry_id]
            else:
                entry = entry_id
                entry_id = entry.id
            if issubclass(type(entry), RoadBlock):
                if entry_id in self.roads:
                    if SlTrace.trace("delete"):
                        SlTrace.lg("delete road: %d" % entry_id)
                    road = self.roads[entry_id]
                    self.clear_selected_block(entry_id)
                    road.remove_display_objects()
                    del self.roads[entry_id]
            else:
                if entry_id in self.cars:
                    if SlTrace.trace("delete"):
                        SlTrace.lg("delete car: %d" % entry_id)
                    self.clear_selected_block(entry_id)
                    car = self.cars[entry_id]
                    car.remove_display_objects()
                    del self.cars[entry_id]
             
            
    def display(self):
        """ Display thing as a list of components
        """
        
        """ Do panel
        """
        super().display()
        for road in self.roads.values():
            road.display()
        for car in self.cars.values():
            car.display()


    def get_race_track(self):
        """ Get top level controler
        """
        if self.container is not None:
            return self.container
        
        return self
    
    
    def get_road(self, road_id):
        """ Get road on track
        """
        if road_id in self.roads:
            return self.roads[road_id]
        
        return None
        

    def get_entry_at(self, x=None, y=None, entry_type=None, all=False, margin=None):
        """ Return car/road at canvas coordinates
        :x: x canvas coordinate
        :y: y canvas coordinate
        :entry_type: get only entries of this type "car", "road"
                default: all types
        :all: if True return list of all entries which contain this coordinate
              if False just first block found which contains this coordinate
        :margin: +=margin in x,y Looing for x-margin to x+margin, y same
        :returns: if all - returns list of all entries found
                    else - returns entry found, else None
        """
        entries_found = []
        if entry_type is None or entry_type == "car":
            for entry in self.cars.values():
                if entry.is_at(x=x, y=y, margin=margin):
                    entries_found.append(entry)
                    if not all:
                        break
        if all or len(entries_found) == 0:
            if entry_type is None or entry_type == "road":
                for entry in self.roads.values():
                    if entry.is_at(x=x, y=y, margin=margin):
                        entries_found.append(entry)
                        if not all:
                            break
        if all:
            return entries_found
        
        if entries_found:
            return entries_found[0]
        
        return None
            

    def get_road_surface(self):
        return self.surface
        

    def get_car_width(self):
        """ Get car width with respect to container
        """
        return self.car_width
        

    def get_road_width(self):
        """ Get road width in with respect to container
        """
        return self.road_width
        

    def get_road_width_feet(self):
        """ Get road width in feet
        """
        return self.road_width_feet
        

    def get_road_width_pixel(self):
        """ Get road width in pixels
        """
        w = self.road_width
        wpi = w * self.get_cv_width()
        return wpi
        

    def get_car_length(self):
        """ Get car length with respect to container
        """
        return self.car_length
        

    def get_road_length(self):
        """ Get road length with respect to container
        """
        return self.road_length
        

    def get_road_length_pixel(self):
        """ Get road length in pixels
        """
        l = self.road_length    # Scale against track/canvas width
        lpi = l * self.get_cv_width()
        return lpi


    def get_minimum_speed(self):
        """ Minimum driving speed for car
        in mph
        """
        return self.minimum_speed


    def get_maximum_speed(self):
        """ Maximum driving speed for car
        in mph
        """
        return self.maximum_speed


    def get_turn_speed(self):
        """ Maximum driving speed for car
        in mph
        """
        return self.turn_speed
        

    def get_road_rotation(self):
        """ Get road rotation in degrees
        Adds in  container or track rotation if any
        :returns: None if no rotation
        """
        return self.rotation
    
        
if __name__ == "__main__":
    import os
    import sys
    from tkinter import *    
    import argparse
    
    from road_block import RoadBlock
    from road_turn import RoadTurn
    from block_arc import BlockArc

    
    
    width = 600     # Window width
    height = width  # Window height
    rotation = None # No rotation
    pos_x = None
    pos_y = None
    parser = argparse.ArgumentParser()
    dispall = False      # Display every change
    dispall = True
    
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
    
    SlTrace.setFlags("short_points")
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
        
    tR = RoadTrack(tag="road_track",
                   canvas=canvas, width=th_width, height=th_height,
                   position=position,
                   cv_width=width, cv_height=height,
                   rotation=rotation)
    tR.display()

    text_pos = Pt(.9,.9)
    text_pi_x = 0
    text_pi_y = -.1
    text_box = BlockText(container=tR, text="text here", position=text_pos)
    tR.comps.append(text_box)
    tR.display()
    
    chk_pi_x = 0
    chk_pi_y = -.1
    chk_pos = Pt(text_pos.x+chk_pi_x, text_pos.y+chk_pi_y)
    chk_width = .05
    chk_height = .05
    
    '''
    chk_pos = Pt(.5,.5)     # HACK to see it
    chk_width = .5
    chk_height = .5
    '''
    
    '''check_box = BlockCheck(container=tR, tag="check", width=chk_width,
                           height=chk_height, position=chk_pos,
                           fill1="black", fill2="white")
    tR.comps.append(check_box)
    tR.display()
    SlTrace.lg("After Checkbox")
    tR.display()
    '''

    turn_arc = 90
    rot1 = -10.
    pos1 = Pt(.5, .25)
    strait_road1 = RoadStrait(tR, tag="first_road",
                             rotation=rot1,
                             position=pos1)
    tR.add_roads(strait_road1)    
    tR.display()
    early_stop = True
    early_stop = False
    if early_stop:
        mainloop()



    
    corn_rot1 = rot1
    corn_pos1 = strait_road1.get_top_left()
    turn_road1 = RoadTurn(tR, tag="road_turn1",
                             arc=turn_arc,
                             rotation=corn_rot1,
                             position=corn_pos1)
    tR.add_roads(turn_road1)
        
    strait_after_turn1 = RoadStrait(tR, tag="after_turn",
                             rotation=corn_rot1+turn_arc,
                             ###position=turn_road1.get_top_left())
                             position=strait_road1.get_top_left())      #Hack
    tR.add_roads(strait_after_turn1)
    
    extend_rot1 = rot1
    extend_pos1 = strait_road1.get_relative_point(Pt(0,-1))     # before
    ###extend_pos1 = strait_road1.get_relative_point(Pt(1,1))      # up to right
    extend_road1 = RoadStrait(tR, tag="road_extend5",
                             rotation=extend_rot1,
                             position=extend_pos1)
    tR.add_roads(extend_road1)
    
    
    cir_pos = Pt(chk_pos.x+chk_pi_x, chk_pos.y+chk_pi_y)
    cir_pi_x = 0
    cir_pi_y = -.1
    circle1 = BlockArc(container=tR, tag="cirlce", radius=.05, arc=360., position=cir_pos)
    tR.comps.append(circle1)
    

    cir_pos = Pt(cir_pos.x+cir_pi_x, cir_pos.y+cir_pi_y)
    circle1 = BlockArc(container=tR, tag="cirlce", radius=.05, rotation=30, arc=360., position=cir_pos)
    tR.comps.append(circle1)

    cir_pos = Pt(cir_pos.x+cir_pi_x, cir_pos.y+cir_pi_y)
    circle1 = BlockArc(container=tR, tag="cirlce3", radius=.03, arc=90., position=cir_pos)
    tR.comps.append(circle1)
    
    cir_pos = Pt(cir_pos.x+cir_pi_x, cir_pos.y+cir_pi_y)
    circle1 = BlockArc(container=tR, tag="cirlce3", radius=.03, arc=180., position=cir_pos)
    tR.comps.append(circle1)
    
    cir_pos = Pt(cir_pos.x+cir_pi_x, cir_pos.y+cir_pi_y)
    circle1 = BlockArc(container=tR, tag="cirlce3", radius=.03, rotation=30, arc=180., position=cir_pos)
    tR.comps.append(circle1)
    
    cir_pos = Pt(cir_pos.x+cir_pi_x, cir_pos.y+cir_pi_y)
    circle1 = BlockArc(container=tR, tag="cirlce2", radius=.025, arc=270., position=cir_pos)
    tR.comps.append(circle1)
    
    cir_pos = Pt(cir_pos.x+cir_pi_x, cir_pos.y+cir_pi_y)
    circle1 = BlockArc(container=tR, tag="cirlce2", radius=.025, rotation=30, arc=270., position=cir_pos)
    tR.comps.append(circle1)
        
    if dispall: tR.display()

    rot2 = 30.
    pos2 = Pt(.1, .2)
    strait_road2 = RoadStrait(tR, tag="second_road",
                             rotation=rot2,
                             position=pos2)
    tR.add_roads(strait_road2)    
    if dispall: tR.display()
    
    corn_rot2 = rot2
    corn_pos2 = strait_road2.get_top_left()
    turn_road2 = RoadTurn(tR, tag="road_turn",
                             arc=turn_arc,
                             rotation=corn_rot2,
                             position=corn_pos2)
    tR.add_roads(turn_road2)    
    if dispall: tR.display()
    
    extend_rot2 = rot2
    extend_pos2 = strait_road2.get_relative_point(Pt(0,-1))     # before
    extend_road2 = RoadStrait(tR, tag="road_extend2",
                             rotation=extend_rot2,
                             position=extend_pos2)
    tR.add_roads(extend_road2)    
    if dispall: tR.display()

    
    rot3 = 90.
    pos3 = Pt(.75, .75)
    strait_road3 = RoadStrait(tR, tag="road3",
                             rotation=rot3,
                             position=pos3)
    tR.add_roads(strait_road3)    
    if dispall: tR.display()
    
    corn_rot3 = rot3
    corn_pos3 = strait_road3.get_relative_point(Pt(0,1))
    turn_road3 = RoadTurn(tR, tag="road_turn",
                             arc=turn_arc,
                             rotation=corn_rot3,
                             position=corn_pos3)
    tR.add_roads(turn_road3)    
    if dispall:  tR.display()
    
    extend_rot3 = rot3
    extend_pos3 = strait_road3.get_relative_point(Pt(0,-1))     # before
    extend_road3 = RoadStrait(tR, tag="road_extend3",
                             rotation=extend_rot3,
                             position=extend_pos3)
    tR.add_roads(extend_road3)    
    if dispall: tR.display()

    
    rot4 = 135.
    pos4 = Pt(.25, .75)
    strait_road4 = RoadStrait(tR, tag="road4",
                             rotation=rot4,
                             position=pos4)
    tR.add_roads(strait_road4)    
    if dispall:  tR.display()
    
    corn_rot4 = rot4
    corn_pos4 = strait_road4.get_top_left()
    turn_road5 = RoadTurn(tR, tag="road_turn4",
                             arc=turn_arc,
                             rotation=corn_rot4,
                             position=corn_pos4)
    tR.add_roads(turn_road5)    
    if dispall:  tR.display()
    
    extend_rot4 = rot4
    extend_pos4 = strait_road4.get_relative_point(Pt(0,-1))     # before
    extend_road4 = RoadStrait(tR, tag="road_extend4",
                             rotation=extend_rot4,
                             position=extend_pos4)
    tR.add_roads(extend_road4)    
    if dispall:  tR.display()
 
    
    rot5 = 30.
    pos5 = Pt(.5, .5)
    strait_road5 = RoadStrait(tR, tag="road5",
                            rotation=rot5,
                            position=pos5)
    tR.add_roads(strait_road5)    
    if dispall: tR.display()
    
    corn_rot5 = rot5
    corn_pos5 = strait_road5.get_top_left()
    turn_road5 = RoadTurn(tR, tag="road_turn5",
                             arc=turn_arc,
                             rotation=corn_rot5,
                             position=corn_pos5)
    tR.add_roads(turn_road5)    
    if dispall: tR.display()
    
    extend_rot5 = rot5
    extend_pos5 = strait_road5.get_relative_point(Pt(0,-1))     # before
    extend_road5 = RoadStrait(tR, tag="road_extend5",
                             rotation=extend_rot5,
                             position=extend_pos5)
    tR.add_roads(extend_road5)    
    tR.display()
    
    mainloop()