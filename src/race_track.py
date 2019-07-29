# race_track.py        
"""
Basis of a race track
Includes RoadTrack with road and car bins
"""
from tkinter import *
from homcoord import *
import copy

from select_trace import SlTrace
from select_error import SelectError

from road_track import RoadTrack
from block_panel import BlockPanel
from block_block import BlockBlock,BlockType,SelectInfo
from block_polygon import BlockPolygon
from block_arrow import BlockArrow
from road_block import RoadBlock,SurfaceType
from road_strait import RoadStrait
from road_turn import RoadTurn
from road_panel import RoadPanel
from car_block import CarBlock
from car_simple import CarSimple
from block_mouse import BlockMouse
from car_race import CarRace,CarInfo



class SnapShot:
    """ Snap shot info to provide undo info
    """
    def __init__(self):
        self.cars = {}
        self.roads = {}
        self.selects_list = []    


class TrackAdjustment:
    """ Information to control track building adjustments
    """
    
    def __init__(self, race_track, block, addition_blocks=[], shifting_blocks=[], undo_blocks=[]):
        """ Setup selection blocks
        :race_track: connection to race track for info and control
        :block: block, arround which adjustments are made
        :addition_blocks: list of blocks, one of which, if selected, adds the corresponding block to the track
        :shifting_blocks: list of blocks, one of which, if selected, shifts all the selected blocks in the
                            corresponding direction
        :undo_blocks: list of blocks, one of which, if selected, undoes the previous command
        """
        self.race_track = race_track
        self.block = block
        self.addition_blocks = addition_blocks
        self.shifting_blocks = shifting_blocks
        self.undo_blocks = undo_blocks
        self.show_track_adjustments(block)            # Display adjustments
    
    def ck_adjust(self, x=None, y=None):
        """ Check if adjustment has been selected
            and do adjustment if possible
        :x,y: x-y track coordinates of mouse
        :returns: True iff selected and adjustment has been made
        """
        for add_block in self.addition_blocks:
            if add_block.is_at(x,y):
                if self.track_adjust(add_block, "add"):
                    return True
        
        return False
    
    
    def track_adjust(self, ck_block, operation="add"):
        """ Adjust track, if possible
        :ck_block:    Selected block
        :operation: Operation to be performed e.g. "add", "shift", "delete", "undo"
        """
        if operation == "add":
            self.remove_markers()
            new_block = self.race_track.front_add_type(front_block=self.block,
                                 new_type=type(ck_block), modifier=ck_block.get_modifier())
            self.show_track_adjustments(new_block)    # show new adjustments
            return True
        
        raise SelectError("Unrecognized track_adjust operation(%s)" % operation)
        return False

    def remove_markers(self):
        """ Remove adjustment markers' blocks/display
        """
        for block in self.addition_blocks:
            self.race_track.remove_entry(block)
        self.addition_blocks = []    
        for block in self.shifting_blocks:
            self.race_track.remove_entry(block)
        self.shifting_blocks = []    
        for block in self.undo_blocks:
            self.race_track.remove_entry(block)
        self.undo_blocks = []
        self.race_track.track_adjustment = None     # Hide

    def show_track_adjustments(self, block): 
        """ Display distinctly possible adjustment selections
        set/reset race_track.track_adjustment
        :block: around which the selections are placed - close to their possible placement
        """
        race_track = self.race_track
        if race_track.track_adjustment is not None:
            self.remove_markers()
        self.block = block              # Make new focus
        additions = []
        xkwargs = {'fill' : 'red'}
        height = block.get_length()*.5
        ''' Trying arrows
        if issubclass(type(block), RoadTurn):
            height *= 2
        road_strait = race_track.front_place_type(block, new_type=BlockArrow,
                                        display=False, height=height, xkwargs=xkwargs)
        road_strait.move_to(road_strait.get_relative_point(0,1.))
        xkwargs = {'fill' : 'blue'}
        road_left = race_track.front_place_type(block, new_type=BlockArrow, modifier="left", display=False, xkwargs=xkwargs)
        road_left.move_to(road_left.get_relative_point(-.75,0))
        xkwargs = {'fill' : 'green'}
        road_right = race_track.front_place_type(block, new_type=BlockArrow, modifier="right", display=False, xkwargs=xkwargs)
        road_right.move_to(road_left.get_relative_point(1.5,0))
        '''
        if issubclass(type(block), RoadTurn):
            height *= 2
        road_strait = race_track.front_place_type(block, new_type=RoadStrait,
                                        display=False, height=height, xkwargs=xkwargs)
        road_strait.move_to(road_strait.get_relative_point(0,1.))
        xkwargs = {'fill' : 'blue'}
        road_left = race_track.front_place_type(block, new_type=RoadTurn, modifier="left", display=False, xkwargs=xkwargs)
        road_left.move_to(road_left.get_relative_point(-.75,0))
        xkwargs = {'fill' : 'green'}
        road_right = race_track.front_place_type(block, new_type=RoadTurn, modifier="right", display=False, xkwargs=xkwargs)
        road_right.move_to(road_left.get_relative_point(1.5,0))
        road_strait.display()
        road_left.display()
        road_right.display()
        additions.append(road_strait)
        additions.append(road_left)
        additions.append(road_right)
        self.addition_blocks = additions
        race_track.track_adjustment = self      # Mark it so race track can see



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
        BlockMouse.__init__(self)
        # Calculate bin dimensions, as fractions of canvas
        # Attempt to give fixed bin thickness
        bin_offset = 2.         # Offset from edge
        cv_height = self.get_cv_height()
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
        track_width = 1. - car_bin_width - offset_x
        track_height = 1. - road_bin_height - offset_y
        car_bin_position = Pt(offset_x, road_bin_height)
        road_bin_position = Pt(car_bin_width, offset_y)
        SlTrace.lg("car_bin size: width=%.1f(%.1f) height=%.1f( %.1f)" %
                    (self.width2pixel(car_bin_width),car_bin_width, self.height2pixel(car_bin_height), car_bin_height))
        SlTrace.lg("car_bin pos: x=%.1f(%.1f) y=%.1f(%.1f)" %
                    (self.width2pixel(car_bin_position.x),car_bin_position.x, self.height2pixel(car_bin_position.y), car_bin_position.y))
        self.car_bin = RoadPanel(tag="car_bin",
                             container=self, position=car_bin_position,
                             width=car_bin_width, height=car_bin_height,
                             background="lightpink")
         
        self.road_bin = RoadPanel(container=self, position=road_bin_position,
                             width=road_bin_width, height=road_bin_height,
                             background="lightgray")
        SlTrace.lg("road_bin pts: %s" % self.road_bin.get_absolute_points())
        
        self.road_track = RoadTrack(container=self, position=track_position,
                               width=track_width, height=track_height,
                               ncar=self.ncar,
                               background="lightgreen")
        self.set_reset()        # Set reset state - can be changed
        self.set_snap_stack = []
        self.track_adjustment = None    # When set, control track adjustment by mouse positioning
        
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
            
    def key_release(self, event):
        self.ctrl_down = False
        self.alt_down = False
        self.shift_down = False


    def mouse_down(self, event):
        mouse_info = self.get_info(event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
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
        
        if self.track_adjustment is not None:   # Check if adjusting track
            if self.track_adjustment.ck_adjust(x,y):
                return
                
        if self.is_bin_selected():              # Check if adding a car
            bin_block = self.bin_selection
            track_block = self.get_entry_at(x,y)
            if issubclass(type(bin_block), CarBlock) and issubclass(type(track_block), RoadBlock):
                dist = 0
                if issubclass(type(track_block), RoadTurn):
                    dist = .5*track_block.get_length_dist()   # Place in middle
                self.add_to_track(bin_block,x=x, y=y, rotation=track_block.get_rotation_at(dist=dist))
                return

                
        block = self.get_entry_at(x,y)        # If inside a car/road, select it/leave it selected
        if block is not None:
            self.set_selected(block)
            return
        
        if self.is_bin_selected():              # If not in an entry, check to see if we should add a new one here
            block = self.bin_selection
            if issubclass(type(bin_block), RoadBlock):
                self.clear_selected()       # Clear all
            self.add_to_track(block,x=x, y=y)
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
        ###got = event.widget.coords (tk.CURRENT, x, y)
        if not self.is_in_track(x,y):
            return              # Ignore if not in track
        
        SlTrace.lg("in track: move to x=%d y=%d" % (x,y), "motion_down")
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
        SlTrace.lg("up is ignored", "motion")
        return


    def add_to_track(self, block, select=True, display=True, x=None, y=None, **kwargs):
        """ Add duplicate of object in bin(block) to track att current location
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
        if select:
            self.set_selected(new_block.id, keep_old=True)
        if display:
            new_block.display()
        if select and issubclass(type(block), RoadBlock):
            self.show_track_adjustments(new_block)
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
        canvas = self.get_canvas()
        mw = canvas._root()
        mw.event_generate('<Motion>', warp=True, x=track_x, y=track_y)
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
        road_track = self.get_road_track()
        for road in road_track.roads.values():
            snap.roads[road.id] = road.dup(keep_id=True)
        # restore from list
        for selected in self.get_selected(origin="road_track"):
            if selected.block.origin == "road_track":
                snap.selects_list.append(copy.deepcopy(selected))
        if save:
            self.snap_shot_undo_stack.append(snap)
        return snap
        
    def snap_shot_restore(self, snap):
        """ Restore state from snap shot
        :snap: snap shot of state
        """
        road_track = self.get_road_track()
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

    def show_track_adjustments(self, block): 
        """ Setup and Display distinctly possible adjustment selections
        :block: around which the selections are placed - close to their possible placement
        """
        TrackAdjustment(self, block)        # Setup self.track_adjustment
            
    
    def front_place_type(self, front_block, new_type=None, modifier=None, display=False, xkwargs=None, **kwargs):
        """ Add road to front end(top end of most recently selected)
            TBD: Possibly changed to determine end of physically connected string
            Supports Road types, Car types
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
        self.add_entry(new_block)
        if display:
            new_block.display()
        return new_block
        
    def add_entry(self, entries):
        """ Add cas/roads to track
        :entries: car/roads to add
        """
        self.road_track.add_entry(entries)




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
        
        self.races = []         # Filled with races, one per entry
        races_by_car_id = {}    # To keep track of cars which have been placed
        races_by_road_id = {}   # To keep track of roads which have been placed
        cars = self.get_cars()
        roads = self.get_roads()
        if len(cars) == 0:
            SlTrace.lg("No cars on track - Please Try again")
            return False
            
        for car in cars:
            road = self.get_car_road(car)
            if road is None:
                SlTrace.lg("car %s is not on road - ignored - please place in road or remove car" % car)
                continue
            
            if road.id in races_by_road_id:
                race = races_by_road_id[road.id]
                race.add_car_info(car, road)
                continue            # Car is part of previously setup race
            
            road_list = self.get_road_list(road)    # Get roads connected to this road in order
            if not self.is_race_circuit(road_list):
                SlTrace.lg("road_list is not a race circuit: %s" % road_list)
                return False
            
            race = CarRace(self, road_list=road_list)
            race.add_car_info(car, road)
            self.races.append(race)
            races_by_car_id[car.id] = race
            for road in road_list:
                races_by_road_id[road.id] = race

        for race in self.races:
            if not race.setup():
                return False
        
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