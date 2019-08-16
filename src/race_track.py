# race_track.py        
"""
Basis of a race track
Includes RoadTrack with road and car bins
"""
from datetime import date
import winsound
from tkinter import *
from homcoord import *
import copy

from select_trace import SlTrace
from select_error import SelectError

from road_block import RoadBlock
from road_track import RoadTrack
from road_strait import RoadStrait
from road_turn import RoadTurn
from road_panel import RoadPanel
from car_block import CarBlock
from car_simple import CarSimple
from block_block import BlockBlock
from block_mouse import BlockMouse
from car_race import CarRace
from track_adjustment import TrackAdjustment, KeyState
from block_commands import BlockCommands


class TRLink:
    def __init__(self, block, id_front=None, id_back=None):
        self.block = block
        self.id_front = id_front
        self.id_back = id_back
    
class  TrackRoadLinks:
    def __init__(self, race_track):
        self.race_track = race_track
        self.links = {}

    def add(self, link):
        block = link.block
        self.links[block.id] = link

    def update_links(self):
        """ Update road links between track segments
        """
        race_track = self.race_track
        for link in self.links.values():
            block = link.block
            if link.id_front is not None:
                block_front = race_track.get_road(link.id_front)
                block.front_road = block_front
                block_front.back_road = block
            if link.id_back is not None:
                block_back = race_track.get_road(link.id_back)
                block.back_road = block_back
                block_back.back_road = block

class SnapShot:
    """ Snap shot info to provide undo info
    """
    def __init__(self):
        self.cars = {}
        self.roads = {}
        self.selects_list = []    
        self.key_state = KeyState.ADD_ROAD
        self.track_adjustment = None        # When set, control track adjustment by mouse positioning
        self.road_groups = []


class RaceTrack(RoadTrack, BlockMouse):
    """
    Race track 
    which can be used to construct a track plus road, track bins
    """
            
    def __init__(self,
                mw=None,
                bin_thick=50,           # Bin thickness in pixels
                **kwargs
                ):
        """ Setup track plus bin
        :update_interval: display update interval (sec)
        if container is None:
            set width, height to pixel(absolute)
        """
        self.snap_shot_undo_stack = []
        self.snap_shot_redo_stack = []
        if mw is None:
            mw = Tk()
        self.mw = mw
        self.motion_bind_id = None
        self.races = []
        self.car_bin = None             # Set if present
        self.road_bin = None
        self.road_track = None
        self.event_block = None         # Set to get very next event
        self.ctrl_down = False          # Initialize key modifier states as off
        self.alt_down = False
        self.shift_down = False
        self.bin_selection = None       # Block to duplicate in track
        self.bin_selected = False       # True ==> clicks on track add duplicate
        super().__init__(**kwargs)
        canvas = self.get_canvas()
        if canvas is None:
            self.canvas = Canvas(width=self.cv_width, height=self.cv_height)
        self.road_groups = [{}]    # Each group is list of roads by block id
        self.cur_road_group = None  # Index of current group, else None
        self.key_state = KeyState.ADD_ROAD
        
        BlockMouse.__init__(self)
        # Calculate bin dimensions, as fractions of canvas
        # Attempt to give fixed bin thickness
        bin_offset = 2.         # Offset from edge
        cv_height = self.get_cv_length()
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
        self.track_position = track_position
        track_width = 1. - car_bin_width - offset_x
        self.track_width = track_width
        track_height = 1. - road_bin_height - offset_y
        self.track_height = track_height
        car_bin_position = Pt(offset_x, road_bin_height)
        road_bin_position = Pt(car_bin_width, offset_y)
        '''SlTrace.lg("car_bin size: width=%.1f(%.1f) height=%.1f( %.1f)" %
                    (self.width2pixel(car_bin_width),car_bin_width, self.height2pixel(car_bin_height), car_bin_height))
        SlTrace.lg("car_bin pos: x=%.1f(%.1f) y=%.1f(%.1f)" %
                    (self.width2pixel(car_bin_position.x),car_bin_position.x, self.height2pixel(car_bin_position.y), car_bin_position.y))
        '''
        self.car_bin = RoadPanel(tag="car_bin",
                             container=self, position=car_bin_position,
                             width=car_bin_width, height=car_bin_height,
                             background="lightpink")
         
        self.road_bin = RoadPanel(container=self, position=road_bin_position,
                             width=road_bin_width, height=road_bin_height,
                             background="lightgray")
        ###SlTrace.lg("road_bin pts: %s" % self.road_bin.get_absolute_points())
        
        self.road_track = RoadTrack(container=self, position=track_position,
                               width=track_width, height=track_height,
                               ncar=self.ncar,
                               background="lightgreen")
        self.set_reset()        # Set reset state - can be changed
        self.set_snap_stack = []
        self.track_adjustment = None    # When set, control track adjustment by mouse positioning


    def add_race_cars(self, ncar=3):
        """ Add race cars to track for race
        :ncar: number of cars to add default: 3
        :returns: True iff OK
        """
        car_idx = 0             # rotate in bin if necessary
        for idx in range(ncar):
            roads = self.get_roads()
            road = roads[0]
            car_bin = self.get_car_bin()
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
            car_abs_position = self.get_absolute_point(car_position)
            SlTrace.lg("car[%d] %s pos:%s[%s]" % (idx, car, car_position, car_abs_position))    
            x,y = road.pts2coords(car_abs_position)
            SlTrace.lg("     coords:[%d,%d]" % (x,y))    
            self.add_to_track(car,x=x, y=y, rotation=road.get_rotation_at(dist=0),
                                    select=False, display=False)
        return True

    def add_to_road_bin(self, road):
        """ Add road to bin
        :road: road instance
            road.position is based on road bin geometry
            road.container will be set to containing entity
        """
        self.road_bin.add_road(road)

    def get_road_bin(self):
        return self.road_bin


    def get_car_bin(self):
        return self.car_bin

    def get_car_road(self, car):
        """ get road containing the car
        Check to see if the car's position lies within a road
        :car: car we are searching for
        :returns: road if found, else None
        """
        coords = car.get_center_coords()
        road = self.get_entry_at(*coords, entry_type="road")
        return road


    def is_pos_in_track(self, position=None):
        """ Check if point (relative to race track container
        is in track area
        :position:    position in track area
        """
        if (position.x < self.track_position.x
             or position.x > self.track_position.x + self.track_width):
            return False
        
        if (position.y < self.track_position.y
             or position.y > self.track_position.y + self.track_height):
            return False
        
        return True

    def get_road_track(self):
        return self.road_track

    def get_road(self, road_id):
        """ Get road on track
        """
        road_track = self.get_road_track()
        if road_track is None:
            return
        
        return road_track.get_road(road_id)


    def get_cars(self):
        road_track = self.get_road_track()
        if road_track is None:
            return []
        
        return list(road_track.cars.values())
    
    
    def get_car_at(self, x=None, y=None, all=False):
        """ Return car at canvas coordinates
        :x: x canvas coordinate
        :y: y canvas coordinate
        :all: if True return list of all roads which contain this coordinate
              if False just first block found which contains this coordinate
        """
        road_track = self.get_road_track()
        if road_track is None:
            return None             # No track yet
        
        cars = road_track.cars
        cars_found = []
        for car in cars.values():
            if car.is_at(x=x, y=y):
                cars_found.append(car)
                if not all:
                    break
        if all:
            return cars_found
        
        if cars_found:
            return cars_found[0]
        
        return None
        

    def get_entry_at(self, x=None, y=None, entry_type=None, all=False, margin=None):
        """ Return road at canvas coordinates
        :x: x canvas coordinate
        :y: y canvas coordinate
        :entry_type: "car", "road" default: any types
        :all: if True return list of all roads which contain this coordinate
              if False just first block found which contains this coordinate
        :margin: += x,y pixels default: None
        """
        road_track = self.get_road_track()
        if road_track is None:
            return None             # No track yet
        
        return road_track.get_entry_at(x=x, y=y, entry_type=entry_type, all=all, margin=margin)
    
    

    def get_event_block(self, types=None, event=None):
        """ get current block associated with current canvas event
        :types: tuplelIf specified, search, in self then container tree,
                for the first occurrence of an object of this/these type/types or derived type
        :event: optional event to check for block
        :returns: Block associated with the current event's tag
                    None if no current canvas/event
        """
        canvas = self.get_canvas()
        if canvas is None:
            return None
        if self.event_block is not None:        # Fast track (HACK?)
            block = self.event_block
            self.event_block = None         # Clear
            return block
        
        item_tags = canvas.find_withtag(CURRENT)
        item_id = None
        if len(item_tags) == 0:
            SlTrace.lg("get_event_block - no CURRENT", "get_event_block")
            if event is not None:
                if SlTrace.trace("event_ignored"):
                    SlTrace.lg("event - none - ignored")
                ###return None
           
                SlTrace.lg("Check for item close", "get_event_block")
                item_id = None
                item = canvas.find_closest(event.x, event.y)
                item_id = item[0]
                for bid in self.selects:
                    selected_info = self.selects[bid]
                    selected_block = selected_info.block
                    canvas_tags = selected_block.get_canvas_tags()
                    if item_id in canvas_tags:
                        if SlTrace.trace("motion"): SlTrace.lg("Found close canvas_tag: %s block %s "
                                    % (item_id,selected_block))
                        break
                if item_id is None:
                    return None
        else:
            item_id = item_tags[0]
            SlTrace.lg("get_event_block: tag:%s" % item_id)
        if item_id is None:
            return None
        
        if not item_id in BlockBlock.tagged_blocks:
            return None
        
        cur_block = BlockBlock.tagged_blocks[item_id]
        SlTrace.lg("tag=%s id=%d" % (item_id, cur_block.id), "tagged block")
        
        if types is not None:
            if not isinstance(types, tuple):
                types = (types)
            tblock = cur_block
            while tblock is not None:
                if isinstance(tblock, types):
                    return tblock
                tblock = tblock.container
            return None         # No such instance
        
        return cur_block


    def get_roads(self):
        road_track = self.get_road_track()
        if road_track is None:
            return []
        
        return list(road_track.roads.values())


    def get_update_interval(self):
        return self.update_interval
    
    
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

    def is_ctrl_down(self):
        return self.ctrl_down

    def is_shift_down(self):
        return self.shift_down

    def is_alt_down(self):
        return self.alt_down
    
    
    def key_down(self,event):
        key = event.keysym
        state = event.state
        ctrl = (state & 0x4) != 0
        alt   = (state & 0x8) != 0 or (state & 0x80) != 0
        shift = (state & 0x1) != 0
        SlTrace.lg("key_down: %s" % key)
        if ctrl:
            self.ctrl_down = True
        else:
            self.ctrl_down = False
        if alt:
            self.alt_down = True
        else:
            self.alt_down = False
        if shift:
            self.shift_down = True
        else:
            self.shift_down = False

        if key.lower() == "g":
            self.snap_shot()
            self.race_start()
            return
        
        if key.lower() == "r":
            self.snap_shot()
            self.reset_cmd()
            return    
        
        if key.lower() == "s":
            self.snap_shot()
            self.race_pause()
            return    

        if key == "space":
            if self.key_state == KeyState.EXTEND_ROAD:
                self.key_state = KeyState.MOVE_GROUP
            elif self.key_state == KeyState.MOVE_GROUP:
                self.key_state = KeyState.EXTEND_ROAD
            if self.track_adjustment is not None:
                self.track_adjustment.change_key_state(self.key_state)      # Change, if required
            return
        

        if self.key_state == KeyState.EXTEND_ROAD and self.track_adjustment == None:
            self.key_state = KeyState.ADD_ROAD      # Force add road
            
        if self.key_state == KeyState.ADD_ROAD:
            self.snap_shot()
            if not self.is_bin_selected() or issubclass(type(self.bin_selection),RoadBlock):
                road = self.road_bin.get_entry(0)
                self.save_bin_selection(road)
                self.set_selected(road.id)
                x = road.get_coords()[0] + 50 
                y = self.road_track.get_coords()[1] - 200
            self.add_to_track(road, x=x,  y=y)
            self.set_key_state(KeyState.EXTEND_ROAD)
            return
        
        elif self.key_state == KeyState.MOVE_GROUP:
            self.snap_shot()
            if self.cur_road_group is not None:
                if self.key_move(self.cur_road_group, key):
                    return
                
            self.beep()
            SlTrace.lg("Can't move road(s) yet - going to EXTEND_ROAD mode")
            self.key_state = KeyState.EXTEND_ROAD
            return
        
        elif self.key_state == KeyState.EXTEND_ROAD:
            if not self.track_adjustment.track_adjust_key(key):
                self.beep()
                SlTrace.lg("Can't adjust track")
                return
            
        return


    def key_move(self, group_index, key):
        """ Move all members of group based on key
        :group_index: index in self.road_groups
        :key:  key indicating movement: left, right, up, down (??? delete, dup???
        """
        head_block = self.get_head_block()
        self.remove_adj_markers()
        road_group = self.road_groups[group_index]
        if len(road_group) == 0:
            return False                #Nothing in group
        
        road1 = next(iter(road_group.values()))    # Use dimensions of first one
        width = road1.get_width()
        height = road1.get_length()
        
        for road in road_group.values():
            if key == "Up":
                pos_adj =  Pt(0, height)
            elif key == "Left":
                pos_adj =  Pt(-width, 0)
            elif key == "Down":
                pos_adj =  Pt(0, -height)
            elif key == "Right":
                pos_adj =  Pt(width, 0)
            else:
                self.beep()
                SlTrace.lg("Unrecognized group move key %s" % key)
                return False
            position = road.get_position()
            position += pos_adj
            road.set_position(position=position)
            road.display()
        if head_block is not None:
            self.show_track_adjustments(head_block)
        return True


    def get_head_block(self):
        if self.track_adjustment is None:
            return None
        
        return self.track_adjustment.block
    

    def remove_adj_markers(self):
        """ Remove any current adjustment visual aids
        """
        if self.track_adjustment is not None:
            self.track_adjustment.remove_markers()
            

    def group_start_add(self, road):
        """ start a group of connected roads or add to existing group
        :road: road to be added
        """
        found = False   # set True if connected to existing block within an existing group
        for group in self.road_groups:
            for road_id in group:
                if road_id == road.id:
                    found = True
                    break
            if found:
                break
        if not found:
            new_group = {}          # create a new group
            new_group[road.id] = road
            self.road_groups.append(new_group)    

            
    def key_release(self, event):
        self.ctrl_down = False
        self.alt_down = False
        self.shift_down = False


    def mouse_down(self, event):
        mouse_info = self.get_info(event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        if SlTrace.trace("mouse_click"):
            SlTrace.lg("mouse_down at x=%d y=%d shift_down=%s" % (x,y, self.is_shift_down()))
        self.snap_shot()
        if self.is_in_track(x,y):
            return self.mouse_down_track(event)
        
        if self.is_in_car_bin(x,y):
            return self.mouse_down_car_bin(event)
        
        if self.is_in_road_bin(x,y):
            return self.mouse_down_road_bin(event)
        
        if SlTrace.trace("mouse_click"):
            SlTrace.lg("Clicked OUTSIDE at x=%d y=%d shift_down=%s" % (x,y, self.is_shift_down()))
        return True


    def get_mw(self):
        """ Get main widget
        """
        canvas = self.get_canvas()
        mw = canvas._root()
        return mw

    def move_cursor_motion(self, event):
        self.move_cursor_x = event.x
        self.move_cursor_y = event.y
        
    def move_cursor(self, x=None, y=None):
        """ Move cursor, waiting till change completes
        :x: x-coordinate
        :y: y-coordinate
        """
        mw = self.get_mw()
        mw.bind("<Motion>", self.move_cursor_motion)       # For generated events
        mw.event_generate('<Motion>', warp=True, x=x, y=y)
        self.wait_move_cursor(x, y)
        mw.unbind("<Motion>")

    def wait_move_cursor(self, x, y):
        mw = self.get_mw()
        ncount = 0
        max_count = 3
        while x != self.move_cursor_x and y != self.move_cursor_y:
            ncount += 1
            if ncount > max_count:
                SlTrace.lg("wait_move_cursor count(%d) exceeded max (%d) exiting" % (ncount, max_count))
                return
            
            SlTrace.lg("wait_move_cursor at %s" % [self.move_cursor_x, self.move_cursor_y])
            mw.after(10)
        SlTrace.lg("wait_move_cursor complete at %s" % ([x,y]))
        
        
    def mouse_down_track(self, event):
        mouse_info = self.get_info(event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        if SlTrace.trace("mouse_click"):
            SlTrace.lg("Clicked at x=%d y=%d shift_down=%s" % (x,y, self.is_shift_down()))
        if self.is_shift_down():                # Shift is grouping control
            block = self.get_entry_at(x,y)
            if block is not None:
                if block.is_selected():
                    self.clear_selected(block.id)
                else:
                    self.set_selected(block.id, x_coord=x,
                                       y_coord=y,keep_old=True)
                return
            else:
                SlTrace.lg("No entry found at x=%d  y=%d" % (x,y))
            return
        
        ''' Don't use down click
        if self.track_adjustment is not None:   # Check if adjusting track
            if self.track_adjustment.ck_adjust(x,y):
                return
        '''
               
        if self.is_bin_selected():              # Check if adding a car
            bin_block = self.bin_selection
            if issubclass(type(bin_block), CarBlock):
                track_block = self.get_entry_at(x,y)
                if track_block is None:
                    SlTrace.lg("No road on which to place the car %s" % bin_block)
                    return
                
                if issubclass(type(bin_block), CarBlock) and issubclass(type(track_block), RoadBlock):
                    dist = 0
                    if issubclass(type(track_block), RoadTurn):
                        dist = .5*track_block.get_length_dist()   # Place in middle
                    self.add_to_track(bin_block,x=x, y=y, rotation=track_block.get_rotation_at(dist=dist))
                    self.clear_bin_selection()
                    return
                return
            
            if issubclass(type(bin_block), RoadBlock):
                self.clear_selected()       # Clear all
                self.add_to_track(bin_block, x=x, y=y)
                self.clear_bin_selection()
                return
        
        self.clear_selected()       # Clear all
        return                  # End of in track operation


 
 
    def mouse_down_car_bin(self, event):    
        """ Mouse event in car bin
        :event: mouse event
        :returns: True iff successful
        """        
        mouse_info = self.get_info(event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        if SlTrace.trace("mouse_click"):
            SlTrace.lg("Clicked car_bin at x=%d y=%d shift_down=%s" % (x,y, self.is_shift_down()))
        mouse_block = self.get_event_block(types=(CarSimple))
        if mouse_block is not None:
            SlTrace.lg("Clicked block[%s]:%s at x=%d y=%d" % (mouse_block.get_tag_list(), mouse_block, x,y))
            self.save_bin_selection(mouse_block)
            self.set_selected(mouse_block.id)
            return True
        
        self.clear_bin_selection()
        return True


    def mouse_down_road_bin(self,event):
        """ Mouse event in road bin
        :event: mouse event
        :returns: True iff successful
        """        
        mouse_info = self.get_info(event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        if SlTrace.trace("mouse_click"):
            SlTrace.lg("Clicked road_bin at x=%d y=%d shift_down=%s" % (x,y, self.is_shift_down()))
        mouse_block = self.get_event_block(types=(RoadStrait,RoadTurn))
        if mouse_block is not None:
            SlTrace.lg("Clicked block[%s]:%s at x=%d y=%d" % (mouse_block.get_tag_list(), mouse_block, x,y))
            self.save_bin_selection(mouse_block)
            self.set_selected(mouse_block.id)
            return True
        
        self.clear_bin_selection()
        return True
        

    def clear_bin_selection(self):
        """ clear selection 
        """
        if self.bin_selection is not None:
            self.clear_selected(self.bin_selection.id)
            self.bin_selection = None
        self.bin_selected = False
        

    def save_bin_selection(self, block):
        """ Save selection to drive next car track click - add duplicate to track
        :block: block to duplicate on track
        """
        self.bin_selection = block      # Note not duplicated yet
        self.bin_selected = True

    def is_bin_selected(self):
        return self.bin_selected
    
    
    def is_in_track(self, x=None,y=None):
        """ Check if point (canvas coordinates) is in road track
        :x,y: x,y canvas coordinates
        """
        track = self.get_road_track()
        if track is None:
            return None
        
        return track.is_at(x=x, y=y)
    
    
    def is_in_car_bin(self, x=None,y=None):
        """ Check if point (canvas coordinates) is in card bin
        :x,y: x,y canvas coordinates
        """
        bin = self.get_car_bin()
        if bin is None:
            return None
        
        return bin.is_at(x=x, y=y)
    
    
    def is_in_road_bin(self, x=None,y=None):
        """ Check if point (canvas coordinates) is in road bin
        :x,y: x,y canvas coordinates
        """
        bin = self.get_road_bin()
        if bin is None:
            return None
        
        return bin.is_at(x=x, y=y)
    
                
    def mouse_down_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        mouse_info = self.get_info(event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        if SlTrace.trace("mouse_click"):
            SlTrace.lg("mouse_down_motion at x=%d y=%d shift_down=%s" % (x,y, self.is_shift_down()))
        ###got = event.widget.coords (tk.CURRENT, x, y)
        if not self.is_in_track(x,y):
            return              # Ignore if not in track
        
        SlTrace.lg("in track: move to x=%d y=%d" % (x,y), "motion_down")
                
        if self.track_adjustment is not None:   # Check if adjusting track
            if self.track_adjustment.ck_adjust(x,y):
                return
            return                      # Ignore all else during track adjustment
        
        mouse_block = self.get_entry_at(x,y)
        if mouse_block is None:
            return
        selected = self.get_selected(mouse_block)
        if selected is None:
            SlTrace.lg("in track: motion block(%s) is not selected - ignored)" %
                       mouse_block)
            return
        
        prev_x = mouse_info.x_coord_prev 
        delta_x = x - prev_x
        prev_y = mouse_info.y_coord_prev
        delta_y = y - prev_y
        prev_y = y
        mouse_block.drag_block(delta_x=delta_x, delta_y=delta_y, canvas_coord=True)
        if SlTrace.trace("dragged"):
            SlTrace.lg("Dragged %s %s delta_xy=(%d,%d) new_xy=(%d,%d)" %
                    (mouse_block.get_tag_list(), mouse_block, delta_x,delta_y, x,y))
        mouse_block.display()
        selected.x = x
        selected.x_coord_prev = prev_x
        selected.y = y 
        selected.y_coord_prev = prev_y 


    def mouse3_down(self, event=None):
        """ Implement right shift operations
        :event: current event if one
        """
        mouse_info = self.get_info(mouse_no=3, event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        SlTrace.lg("mouse3 down at x=%d y=%d" % (x,y), "motion_to")
        if SlTrace.trace("mouse_right_info"):
            blocks = self.get_entry_at(x=x, y=y, all=True)
            if len(blocks) == 0:
                SlTrace.lg("No cars/roads at xy(%d,%d)" % (x,y))
                return
            
            if len(blocks) > 1:
                SlTrace.lg("%d cars/roads(%s) found at xy(%d,%d)" %
                           (len(blocks), blocks, x,y))
            for block in blocks:
                SlTrace.lg("%s rot: %.0f pos: %s  front add: rot: %.0f pos: %s" %
                           (block, block.get_rotation(), block.get_position_coords(),
                           block.get_front_addon_rotation(), block.abs_front_pos()))
                if block.back_road is not None:
                    SlTrace.lg("    back_road: %s" % block.back_road)
                if block.front_road is not None:
                    SlTrace.lg("    front_road: %s" % block.front_road)
    def mouse3_down_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        mouse_info = self.get_info(mouse_no=3, event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        if not self.is_in_track(x,y):
            return                  # Ignore if not in track
        
        SlTrace.lg("move3 to x=%d y=%d" % (x,y), "motion_to")
        
        selecteds = self.get_selected(origin="road_track")
        for selected in selecteds:
            block = selected.block
            if block is None:
                raise SelectError("mouse_down_motion when selected.block is None")

            # Calculate mouse movement
            prev_x = mouse_info.x_coord_prev 
            delta_x = x - prev_x
            prev_y = mouse_info.y_coord_prev
            delta_y = y - prev_y
            selected.x_prev_coord, selected.y_prev_coord = block.pts2coords(block.get_absolute_position())
            
            block.drag_block(delta_x=delta_x, delta_y=delta_y, canvas_coord=True)
            if SlTrace.trace("dragged"):
                SlTrace.lg("Dragged %s %s delta_xy=(%d,%d) new_xy=(%d,%d)" %
                        (block.get_tag_list(), block, delta_x,delta_y, x,y))
            block.display()
            selected.x, selected.y = block.pts2coords(block.position)
            
            
    def mouse_up (self, event):
        self.is_down = False
        ###event.widget.itemconfigure (tk.CURRENT, fill =self.defaultcolor)
        cnv = event.widget
        x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("up at x=%d y=%d" % (x,y), "motion")
        '''if self.track_adjustment is not None:
            self.track_adjustment.remove_markers()
        '''
        return


    def add_to_track(self, block, select=True, display=True, x=None, y=None, **kwargs):
        """ Add duplicate of object in bin(block) to track at current location
        :block: object(road/car) to add
        :select: Select added block default: True
        :display: display after add
        :x: x bin position in pixels
        :y: y bin position in pixels
        :kwargs: Additional new block creation parameters
        :returns: added block 
        """
        if issubclass(type(block), RoadBlock):
            road_length = self.get_road_length()
            road_width = self.get_road_width()
            if issubclass(type(block),RoadTurn):
                road_length = road_width
            new_block = block.dup(origin="road_track", container=self,
                           width=road_width, height=road_length, radius=road_width, **kwargs)
        else:
            car_length = self.get_car_length()
            car_width = self.get_car_width()
            new_block = block.dup(origin="road_track", container=self,
                           width=car_width, height=car_length, **kwargs)
        self.add_entry(new_block)    
        new_block.set_position(position=Pt(x,y), canvas_coord=True)
        SlTrace.lg("add_to_track: %s at %.2f,%.2f coords: %s"
                    % (new_block, x,y, new_block.get_coords()))
        if select:
            self.set_selected(new_block.id, keep_old=True)
        if display:
            new_block.display()
        if select and issubclass(type(block), RoadBlock):
            self.show_track_adjustments(new_block, x=x, y=y)
        return new_block        

    def move_to_track(self, block, bin_x=None, bin_y=None):
        """ Move object(block) to track from bin
        :block: object to move
        :bin_x: x bin position in pixels
        :bin_y: y bin position in pixels
        """
        if block is None:
            raise SelectError("move_to_track when block is None")
        
        road_rot = -90.
        track = self.get_road_track()
        track_pos = Pt(block.position.x, .2) # Fixed as lower left corner for now
        SlTrace.lg("move_to_track: from %s[%s] xy=(%d,%d)" %
         (block, block.get_tag_list(), bin_x,bin_y))
        if block.origin == "road_track":
            SlTrace.lg("%s is already in road_track - ignore request" % block)
            return

        self.clear_selected(block.id)
        block.display()             # Hack to change tag        
        if isinstance(block, RoadStrait):
            track_block = RoadStrait(track,
                                     rotation=road_rot,
                                     position=track_pos, origin="road_track")
        elif isinstance(block, RoadTurn):
            track_block = RoadTurn(track,
                                     rotation=road_rot,
                                     position=track_pos, origin="road_track")

        self.add_entry(track_block)
        track_abs_pos = track_block.get_absolute_point(track_pos)
        track_block_coord = track.pts2coords(track_abs_pos)
        track_x,track_y = track_block_coord
        self.move_cursor(track_x, track_y)
        self.clear_selected(block.id)
        self.set_selected(track_block.id, x_coord=track_x, y_coord=track_y)
        track_block.display()
        SlTrace.lg("move_to_track: %s[%s] xy=(%d,%d)" %
         (track_block, track_block.get_tag_list(), track_x,track_y))
        track_block.status = "new_to_track"
        ###self.set_event_block(track_block)   # Set for very next event
        ###mw.event_generate('<ButtonPress-1>', warp=True, x=track_x, y=track_y)   # Simulate down click
        ###mw.event_generate('<B1-Motion>', warp=True, x=track_x, y=track_y)   # Simulate down click
        

    def set_event_block(self, block):
        """ Set for very next event
        forcing this block
        :block: for this event
        """
        SlTrace.lg("Setting event block: %s" % block)
        self.event_block = block 


    def snap_shot(self, save=True):
        """ snap shot of race_track state to
        shallow info only just delete, select info preserved
        restrict to origin == "road_track"
        implement simple do/undo
        :save: if True, save snap shot on undo stack
        :returns: snap shot of state
        """
        snap = SnapShot()
        snap.key_state = self.key_state
        road_track = self.get_road_track()
        for road in road_track.roads.values():
            snap.roads[road.id] = road.dup(keep_id=True)
        for car in road_track.cars.values():
            snap.cars[car.id] = car.dup(keep_id=True)
        # restore from list
        for selected in self.get_selected(origin="road_track"):
            if selected.block.origin == "road_track":
                snap.selects_list.append(copy.deepcopy(selected))
        snap.cur_road_group = self.cur_road_group
        snap.road_groups = []
        for group in self.road_groups:
            snap.road_groups.append(group)
            
        if save:
            self.snap_shot_undo_stack.append(snap)
        return snap
        
    def snap_shot_restore(self, snap):
        """ Restore state from snap shot
        :snap: snap shot of state
        """
        road_track = self.get_road_track()
        self.track_adjustment = snap.track_adjustment       # Block ???
        self.key_state = snap.key_state
        self.clear_selected(origin="road_track", display=True)
        self.remove_entry(list(road_track.roads.values()))            
        self.remove_entry(list(road_track.cars.values()))            
        self.add_entry(list(snap.roads.values()))
        self.add_entry(list(snap.cars.values()))
        id_list = []
        for selects in snap.selects_list:
            id_list.append(selects.block.id)
        if SlTrace.trace("snap_shot"):
            SlTrace.lg("snap_shot_restore selects_list len: %d, %s" %
                        (len(snap.selects_list), id_list))
        for selected in snap.selects_list:
            self.set_selected(selected.block.id, x_coord=selected.x_coord, y_coord=selected.y_coord,
                              x_coord_prev=selected.x_coord_prev, y_coord_prev=selected.y_coord_prev,
                              keep_old=True)
        self.road_groups = []
        for group in snap.road_groups:
            self.road_groups.append(group)
        self.cur_road_group = snap.cur_road_group

        for road in snap.roads.values():
            road.display()
            
            
    def pos_change_control_proc(self, change):
        """ Part position change control processor
        :change: identifier (see PositionWindow)
        """
        if change == "undo_cmd":
            return self.undo_cmd()
        
        if change == "redo_cmd":
            return self.redo_cmd()
        
        self.snap_shot()
        if change == "reset_track":
            return self.reset_cmd()
        
        if change == "set_track":
            return self.set_cmd()
        
        
        selected_blocks = self.get_selected_blocks()
        len_sels = len(selected_blocks)
        sel_block = None        # Set to block iff only selected
        ltdeg = 90.
        if len_sels > 0:
            sel_block = selected_blocks[-1]
        
        if change == "spin_left":
            if sel_block:
                sel_block.rotate(ltdeg)
                SlTrace.lg("%s rotation: %.0f" % (sel_block, sel_block.rotation))
                sel_block.display()
        elif change == "spin_right":
            if sel_block:
                sel_block.rotate(-ltdeg)
                SlTrace.lg("%s rotation: %.0f" % (sel_block, sel_block.rotation))
                sel_block.display()
        elif change == "flip_up_down" or change == "flip_left_right":
            if sel_block:
                if isinstance(sel_block, RoadTurn):
                    ###sel_block.rotate(180)
                    ###sel_block.display()
                    sel_block.new_arc(-sel_block.get_arc())
        elif change == "front_add_strait":
            self.front_add_type(RoadStrait)
        elif change == "front_add_left_turn":
            self.front_add_type(RoadTurn, "left")
        elif change == "front_add_right_turn":
            self.front_add_type(RoadTurn, "right")
        elif change == "front_add_red_car":
            self.front_add_type(CarSimple, "red")
        elif change == "front_add_blue_car":
            self.front_add_type(CarSimple, "blue")
        elif change == "back_add_strait":
            self.back_add_type(RoadStrait)
        elif change == "back_add_left_turn":
            self.back_add_type(RoadTurn, "left")
        elif change == "back_add_right_turn":
            self.back_add_type(RoadTurn, "right")
        elif change == "select_none":
            self.select_none()
        elif change == "select_all":
            for road in self.road_track.roads.values():
                road_id = road.id
                self.set_selected(road_id, keep_old=True)
                road.display()
        elif change == "select_others":
            for road in self.road_track.roads.values():
                road_id = road.id
                if road.is_selected():
                    self.clear_selected_block(road_id)
                else:
                    self.set_selected(road_id, keep_old=True)
                road.display()
        elif change == "delete_selected":
            for entry in self.get_selected_blocks(origin="road_track"):
                self.remove_entry(entry.id)
        elif change == "delete_all":
            self.remove_entry(list(self.road_track.roads.values()))
            self.remove_entry(list(self.road_track.cars.values()))
        else:
            SlTrace.lg("position_change_control_proc: change(%s) not yet implemented" % change)
            return False        # Unsuccessful

        return True                 # Successful


    def select_none(self):
        selected_blocks = self.get_selected_blocks()
        for block in selected_blocks:
            self.clear_selected(block.id)
            block.display()

    def set_reset(self):
        """ Set current state as "reset" state - to be
            returned to upon "reset" cmd
        """
        self.reset_snap = self.snap_shot(save=False)


    def reset_cmd(self):
        SlTrace.lg("reset_cmd")
        if self.reset_snap is None:
            SlTrace.lg("Can't reset")
            return False
        set_snap = self.snap_shot(save=False)   # save for set cmd
        self.set_snap_stack.append(set_snap)    # set reclaims state before reset
        self.snap_shot_restore(self.reset_snap)
                                                # Simple, unundoable settings
        self.road_groups = []                   # Each group is a dictionary of roads by block id
        self.cur_road_group = None              # Index of current group, else None
        self.key_state = KeyState.ADD_ROAD
        self.races = []
        return True


    def road_room_check(self, road_block, road_type=None, modifier=None, over_road_ok=False):
        """ Check if adding a new block if possible doesn't go over edge or get so close
        that another road operation is not possible
        :road_block: current road
        :road_type:  road type(class)
        :modifier: left/right
        :over_road_ok:  ok to go over other road segment
        """
        front_block = road_block
        if issubclass(road_type, RoadStrait):
            add_pos = front_block.get_front_addon_position(nlengths=2.55)
            if not self.is_pos_in_track(position=add_pos):
                return False
            
        else:
            add_pos = front_block.get_front_addon_position()
            add_rot = front_block.get_front_addon_rotation()
            if modifier == "left":
                new_pt = Pt(-.55, 1.)        # Turning distance
            else:
                new_pt = Pt(1.55, 1.)
            turn_pos = front_block.get_relative_point(new_pt)
            if not self.is_pos_in_track(position=turn_pos):
                return False
        
        if not over_road_ok:
            in_front_coords = front_block.get_infront_coords()
            x,y = in_front_coords[0],in_front_coords[1]
            entries = self.get_entry_at(x,y, all=True)
            adj_block = None
            if self.track_adjustment is not None:
                adj_block = self.track_adjustment.adj_block
            for entry in entries:
                if adj_block is None or entry.id != adj_block.id:
                    SlTrace.lg("Would hit entry %s" % entry)
                    return False
                
        return True
    

    def set_cmd(self):
        SlTrace.lg("set_cmd")
        if not self.set_snap_stack:
            SlTrace.lg("No reset yet - Can't set")
            return False
        set_snap = self.set_snap_stack.pop()
        self.snap_shot_restore(set_snap)
        return True


    def undo_cmd(self):
        SlTrace.lg("undo_cmd")
        if not self.snap_shot_undo_stack:
            SlTrace.lg("Can't undo")
            return False
        redo_snap = self.snap_shot(save=False)   # save for redo
        snap = self.snap_shot_undo_stack.pop()
        self.snap_shot_restore(snap)
        self.snap_shot_redo_stack.append(redo_snap)
        return True

    def redo_cmd(self):
        SlTrace.lg("redo_cmd")
        if not self.snap_shot_redo_stack:
            SlTrace.lg("Can't redo")
            return False
        self.snap_shot()        # So subsequent undo will undo this redo
        snap = self.snap_shot_redo_stack.pop()
        self.snap_shot_restore(snap)
        return True
    
    def remove_entry(self, entries):
        """ Delete cars/roads from race_track
        :entries: track entries/ids to remove
        """
        road_track = self.get_road_track()
        if road_track is None:
            return          # No track
                                            # Remove cars from any races
        if not isinstance(entries, list):
            entries = [entries]         # Make a list of one
        for entry in entries:
            if isinstance(entry, int):
                entry = self.id_blocks[entry]
            if issubclass(type(entry), CarBlock):
                car = entry
                new_races = []
                for race in self.races:
                    car_states = race.car_states
                    if car.id in car_states:
                        del car_states[car.id]
                    if len(car_states) == 0:
                        race.shutdown()         # Shutdown if no cars left
                        continue
                    new_races.append(race)      # Add back in 
                if len(new_races) != self.races:
                    self.races = new_races      # Update with new list
                       
        road_track.remove_entry(entries)
                        
            
    def back_add_type(self, new_type=None, modifier=None):
        """ Add RoadStrait to back end(back end of selected list) to make a new back end
            TBD: Possibly changed to determine end of physically connected string
        """
        sel_list = self.get_selected_blocks()
        if not sel_list:
            return      # None selected
        
        SlTrace.lg("\nback_add_type: new_type:%s modifier:%s" %
                   (new_type, modifier), "add_block")
        back_block = sel_list[0]
        SlTrace.lg("back_add_type: back_block:%s" % back_block, "add_block")
        SlTrace.lg("back_add_type: points:%s" % back_block.get_absolute_points(), "add_block")
        add_pos = back_block.get_back_addon_position(new_type=new_type)
        add_rot = back_block.get_back_addon_rotation(new_type=new_type)
        if SlTrace.trace("add_block"):
            abs_pos = self.get_absolute_point(add_pos)
            SlTrace.lg("back_add_type: front rot:%.0f pos:%s(%s) rot:%.0f" %
                        (back_block.rotation, add_pos, abs_pos, add_rot))
        new_block = back_block.new_type(new_type, modifier)
        if add_rot != new_block.get_rotation():
            new_block.set_rotation(add_rot)   # Small optimization
        self.add_entry(new_block)
        SlTrace.lg("back_add_type: new_block:%s" % new_block, "add_block")
        SlTrace.lg("back_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        new_block.move_to(position=add_pos)
        SlTrace.lg("back_add_type: moved new_block:%s" % new_block, "add_block")
        SlTrace.lg("back_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        ###self.set_selected(new_block, keep_old=True)
        self.set_selected(new_block.id, keep_old=True)
        canvas = self.get_canvas()
        new_block.display()


    def beep(self):
        frequency = 800  # Set Frequency To 2500 Hertz
        duration = 200  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)
        ###mw = self.get_mw()
        ###mw.after(duration)
        
            
    def front_add_type(self, front_block=None, new_type=None, modifier=None):
        """ Add road to front end(top end of most recently selected)
            TBD: Possibly changed to determine end of physically connected string
            Supports Road types, Car types
            :front_block: block(road) to which we add, default: most recently selected
            :new_type: type of addition e.g. RoadTurn
            :modifier: e.g "left", "right"
            :returns: created object
        """
        
        if front_block is None:
            sel_list = self.get_selected_blocks()
            if not sel_list:
                return      # None selected
            front_block = sel_list[-1]
                
        SlTrace.lg("\nfront_add_type: new_type:%s modifier:%s" %
                   (new_type, modifier), "add_block")
        new_block = self.front_place_type(front_block, new_type=new_type, modifier=modifier)
        if front_block.origin == "road_track" and issubclass(type(new_block), CarBlock):
            front_block.link_roads(new_block)
        SlTrace.lg("front_add_type: moved new_block:%s" % new_block, "add_block")
        SlTrace.lg("front_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        ###self.set_selected(new_block, keep_old=True)
        self.set_selected(new_block.id, keep_old=True)
        new_block.display()
        return new_block

    def clear_track_adjustments(self):
        """ Clear track building adjustments
        """
        if self.track_adjustment is not None:
            self.track_adjustment.remove_markers()


    def set_key_state(self, key_state = KeyState.EXTEND_ROAD):
        """ Set key_state
        :key_state: state default: EXTEND_ROAD
        """
        self.key_state = key_state
        
    def show_track_adjustments(self, block, x=None,  y=None): 
        """ Setup and Display distinctly possible adjustment selections
        :block: around which the selections are placed - close to their possible placement
                default use current block, if one
        :x: current mouse coordinate default: current center of block
        :y:
        """
        TrackAdjustment(self, block, x=x, y=y)        # Setup/resetup self.track_adjustment
            
    
    def front_place_type(self, front_block,
                        new_type=None,
                        grouped=True,
                        modifier=None, display=False, xkwargs=None, **kwargs):
        """ Add road to front end(top end of most recently selected)
            TBD: Possibly changed to determine end of physically connected string
            Supports Road types, Car types
            :grouped: Add to current group default: True
            :display: true => display
            :kwargs: args passed to object construction
            :returns: created object
        """
        
        add_pos = front_block.get_front_addon_position()
        add_rot = front_block.get_front_addon_rotation()
        new_block = front_block.new_type(new_type, modifier=modifier, xkwargs=xkwargs, **kwargs)
        if add_pos != new_block.get_position():
            new_block.set_position(add_pos)   # Small optimization
        if add_rot != new_block.get_rotation():
            new_block.set_rotation(add_rot)   # Small optimization
        self.add_entry(new_block, grouped=grouped)
        if display:
            new_block.display()
        return new_block
        
    def add_entry(self, entries, grouped=True):
        """ Add cas/roads to track
        :entries: car/roads to add
        :grouped: Add to current group
        """
        if grouped:
            self.add_to_group(entries)
        self.road_track.add_entry(entries)


    def add_to_group(self, entries, group_index=None):
        """ Add road/car to group
        :entries: one/list of road/cars to be added
        :group_index: group in which to add default: most recent
        """
        if not isinstance(entries, list):
            entries = [entries]

        if len(self.road_groups) == 0:
            self.road_groups.append({})        
        if group_index is None:
            group_index = len(self.road_groups)-1
        while len(self.road_groups) < group_index:
            self.road_groups.append({})
        group = self.road_groups[group_index]
        self.cur_road_group = group_index        
        for entry in entries:
            group[entry.id] = entry
            



    def race_control_proc(self, command):
        """ Race control commands
        """
        if command == "race_setup":
            return self.race_setup()
        
        elif command == "race_start":
            return self.race_start()
        
        elif command == "race_pause":
            return self.race_pause()
        
        elif command == "race_continue":
            return self.race_continue()
        
        elif command == "race_stop":
            return self.race_stop()
        
        elif command == "race_reset":
            self.race_shutdown()
            return True
        
        elif command == "race_faster":
            self.race_faster()
            return True
        
        elif command == "race_slower":
            self.race_slower()
            return True
        
        else:
            SlTrace.lg("command %s is not yet implemented" % command)
        return True                 # Successful
        

    def race_setup(self):
        """ Setup race
        :returns: True iff successful race setup
        
          1. check if any cars in position (on the track)
          2. Check if track(s) is(are) complete (for now complete circuit)
          3. Do any optimizations available
 
        One or more cars per race all cars on same circuit are in that race
        Car must be on a track to race

       """
        self.clear_track_adjustments()
        self.clear_bin_selection()
        self.clear_selected()
        ###self.races = []         # Filled with races, one per entry
        races_by_car_id = {}    # To keep track of cars which have been placed
        races_by_road_id = {}   # To keep track of roads which have been placed
        cars = self.get_cars()
        if len(cars) == 0:
            SlTrace.lg("No cars on track - Adding some to make it interesting!")
            if not self.add_race_cars():
                return False
            cars = self.get_cars()
        for car in cars:
            road = self.get_car_road(car)
            if road is None:
                SlTrace.lg("car %s is not on road - ignored - please place in road or remove car" % car)
                continue
            
            if road.id in races_by_road_id:
                race = races_by_road_id[road.id]
                race.add_car_info(race, car, road)
                continue            # Car is part of previously setup race
            
            road_list = self.get_road_list(road)    # Get roads connected to this road in order
            if not self.is_race_circuit(road_list):
                SlTrace.lg("road_list is not a race circuit: %s" % road_list)
                return False
            
            race = CarRace(self, road_list=road_list)
            race.add_car_info(race, car, road)
            self.races.append(race)
            races_by_car_id[car.id] = race
            for road in road_list:
                races_by_road_id[road.id] = race

        for race in self.races:
            if not race.setup():
                return False
        
        self.set_reset()        # Setup for recovery
        return True
    

    def race_shutdown(self):
        """ Shutdown all races
        """
        for race in self.races:
            race.shutdown()

        cars = self.get_cars()
        for car in cars:
            self.remove_entry(car)


    def get_road_list(self, first_road):
        """ Get all roads connected to this road, in order
        :road: to be uses as the start of a track
        :returns: return a list of the roads in order
        """
        road = first_road
        road_list = []      # start list with this road
        while road is not None:
            if SlTrace.trace("front_road"):
                SlTrace.lg("get_road_list: appending %s" % road)
                SlTrace.lg("       coords: %s" % road.get_coords())
            road_list.append(road)
            road_next = road.get_front_road()    
            if road_next is None:
                if SlTrace.trace("front_road"):
                    SlTrace.lg("get_road_list: no more in chain")
                break               # No more in front ==> End of list
            
            if road_next.id == first_road.id:
                if SlTrace.trace("front_road"):
                    SlTrace.lg("get_road_list: next %s is first_road in list" % (road_next))
                break           # Connected to first ==> End of list
            
            road = road_next
        return road_list

            
    def is_race_circuit(self, road_list, complete=True):
        """ Determine if this road_list is a valid race circuit
        :road_list: list of roads from first road segment to the last segment which abuts the first
        :complete: if True, and first_road is in position, complete circuit link and return True
        :returns: True if valid race_circuit Note: the end may not be linked to the start
        """
        if len(road_list) < 2:
            SlTrace.lg("circuit length(%d) < 2" % len(road_list))
            return False            # One or none
        
        first_road = road_list[0]
        for road in road_list:
            next_road = road.get_front_road()
            if next_road is None:
                if complete and first_road.is_front_of(road):
                    road.link_roads(first_road)
                    return True
                break
            if next_road.id == first_road.id:
                return True         # Already linked
        
        SlTrace.lg("Not a race circuit:")
        for road in road_list:
            SlTrace.lg("%s front_road: %s back_road: %s" % (road, road.get_front_road(), road.back_road))
            road.mark()    
        return False
        
    def get_road_width_feet(self):
        return self.road_width_feet 
    
            
    def race_start(self):
        """ Start race(s)
        """
        if len(self.races) == 0:        # Setup if not already
            if not self.race_setup():
                return False
            
        for race in self.races:
            race.start()
    
    def race_pause(self):
        """ Pause race(s)
        """
        for race in self.races:
            race.pause()
    
    def race_continue(self):
        """ Pause race(s)
        """
        for race in self.races:
            race.race_continue()
    
    def race_stop(self):
        for race in self.races:
            race.stop()
 
    def race_faster(self):
        for race in self.races:
            race.faster()

    def race_slower(self):
        for race in self.races:
            race.slower()


    def save_track_file(self, file_name):
        """ Save current track state to file
        """
        SlTrace.lg("save_track_file %s" % file_name)
        with open(file_name, "w") as fout:
            print("# %s" % file_name, file=fout)
            today = date.today()
            d2 = today.strftime("%B %d, %Y")
            print("# On: %s\n" % d2, file=fout)
            print("from homcoord import *", file=fout)
            print("from road_strait import RoadStrait", file=fout)
            print("from road_turn import RoadTurn", file=fout)
            print("from car_simple import CarSimple", file=fout)
            print("from block_commands import *", file=fout)
            print("", file=fout)
            road_track = self.get_road_track()
            for road in road_track.roads.values():
                road.out_road_cmd(file=fout)
            for car in road_track.cars.values():
                car.out_car_cmd(file=fout)
            # restore from list TBD : save select list ???
            # save groups ??? TBD
        
        return True
            
    def load_track_file(self, file_name):
        """ Load track file
        """
        self.snap_shot()
        SlTrace.lg("load_track_file %s" % file_name)
        self.track_links = TrackRoadLinks(self)
        base_id = 1
        next_id = self.get_next_id()
        if  next_id != base_id:
            next_id += 100 
            next_id = 100 * round(next_id/100) + 1
            self.set_next_id(next_id)
        self.load_track_file_base_id = base_id
        with open(file_name, "r") as fin:
            SlTrace.lg("# %s" % file_name)
            self.load_track_commands = BlockCommands(self, src_file_path=file_name)
            res = self.load_track_commands.procFilePy(file_name)
            self.track_links.update_links()     # Set links between road segments
            return res
        return False

    """
    Track command file  functions
    """
    def car(self, id=None, classtype=None, **kwargs):    
        """ Create road on track, possibly from previously saved road.
            :id: relative block id - actual id will be next suitable id larger than current block id
            :classtype:  type of road e.g. RoadStrait, RoadTurn
            :returns: True iff successful 
        """
        base_id = self.load_track_file_base_id
        id_adj = base_id-1
        if issubclass(classtype, CarSimple):
            new_block = CarSimple(track=self, id=id+id_adj, origin="road_track",
                           **kwargs)
        else:
            raise SelectError("Unsupported car type %s" % classtype)
        self.add_entry(new_block)
        new_block.display()    
        return new_block        
    
    
    
    def road(self, id=None, classtype=None, front_road=None, back_road=None, **kwargs):    
        """ Create road on track, possibly from previously saved road.
            :id: relative block id - actual id will be next suitable id larger than current block id
            :classtype:  type of road e.g. RoadStrait, RoadTurn
            :front_road: link to block in front of this one
            :back_road: link to block in back of this one
            :kwargs: Additional new block creation parameters
            :returns: True iff successful 
        """
        base_id = self.load_track_file_base_id
        id_adj = base_id-1
        our_id = id + id_adj
        if issubclass(classtype, RoadTurn):
            new_block = RoadTurn(track=self, id=id+id_adj, origin="road_track",
                           **kwargs)
        elif issubclass(classtype, RoadStrait):
            new_block = RoadStrait(track=self, id=id+id_adj, origin="road_track",
                           **kwargs)
        else:
            raise SelectError("Unsupported road type %s" % classtype)
        if front_road is not None or back_road is not None:
            link = TRLink(new_block, id_front=front_road, id_back=back_road)
            self.track_links.add(link)
        self.add_entry(new_block)
        new_block.display()    
        return new_block        

    
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