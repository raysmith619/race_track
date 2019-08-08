from tkinter import *
from homcoord import *
from enum import Enum

from select_trace import SlTrace
from select_error import SelectError

from block_arrow import BlockArrow
from block_cross import BlockCross
from road_block import RoadBlock,SurfaceType
from road_strait import RoadStrait
from road_turn import RoadTurn
        
        
class KeyState(Enum):
    ADD_ROAD = 1
    MOVE_GROUP = 2
    EXTEND_ROAD = 3


class TrackAdjustment:
    """ Information to control track building adjustments
    """
    
    def __init__(self, race_track, block,x=None, y=None,
                  adj_block=None, addition_blocks=[], shifting_blocks=[], undo_blocks=[]):
        """ Setup selection blocks
        :race_track: connection to race track for info and control
        :block: block, around which adjustments are made
        :x:    Current mouse position default: center of block
        :addition_blocks: list of blocks, one of which, if selected, adds the corresponding block to the track
        :shifting_blocks: list of blocks, one of which, if selected, shifts all the selected blocks in the
                            corresponding direction
        :undo_blocks: list of blocks, one of which, if selected, undoes the previous command
        """
        self.race_track = race_track
        self.block = block
        self.start_coords = None        # Flag for start
        if x is None:
            [x,y] = block.get_center_coords()
        self.initial_pt = self.block.get_internal_point(coords=[x,y]) 
        self.adj_block = adj_block
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
        if self.start_coords is not None:
            if x != self.start_coords[0] or y != self.start_coords[1]:
                SlTrace.lg("at %s, not yet at start_coords: %s" % ([x,y], self.start_coords))
                self.race_track.move_cursor(self.start_coords[0], self.start_coords[1])        # Force it there
                ###return False
            
            SlTrace.lg("At start coords: %s" % ([x,y]))
            self.initial_coords = self.start_coords
            self.start_coords = None
            self.x_initial = x  
            self.y_initial = y
            self.prev_adjust_x = x      # Don't trigger until movement 
            self.prev_adjust_y = y
                
        block = self.block    
        if x == self.prev_adjust_x and y == self.prev_adjust_y:
            SlTrace.lg("ck_adjust skipping at %.2f,%.2f" % (x,y))
            return False
        SlTrace.lg("ck_adjust at %.2f,%.2f" % (x,y))
        
        self.prev_adjust_x = x 
        self.prev_adjust_y = y
        if self.track_adjust(self.block,x,y):
            return True
        '''else:
            SlTrace.lg("ck_adjust try again at %s" % [x,y])
            self.race_track.move_cursor(*self.initial_coords) # Try again
            if self.block.is_at(x,y):
                if self.track_adjust(self.block,x,y):
                    return True
                return True             # Still in adjustment area
        '''
        return False


    def track_adjust_key(self, key):
        """ Adjust track based on key
        :key: key(keysym) pressed
        :returns: True iff action
        """
        SlTrace.lg("track_adjust_key: %s" % key)
        new_block = None            # Set if adding a new block
                                # Do action based on operators view
                                # not on block's view
                                # TBD: Up goes/continues up, Right goes/continues right 
        block = self.block
        go_rotation = block.get_front_addon_rotation()
        SlTrace.lg("go_rotation: %.1f" % go_rotation)
        if key == "Up":
            new_rotation = 0.
        elif key == "Left":
            new_rotation = 90.
        elif key == "Down":
            new_rotation = 180.
        elif key == "Right":
            new_rotation = 270.
        else:
            SlTrace.lg("Unsupported key %s" % key)
            return False
        
        chg_rotation = (360. + new_rotation-go_rotation) % 360.
        SlTrace.lg("chg_rotation: %.1f" % chg_rotation)
        ang_close = .1
        
        if abs(chg_rotation) < ang_close:   # 0 
            self.snap_shot()
            SlTrace.lg("track_adjust: Adding RoadStrait")
            if not self.add_new_block(RoadStrait):
                return False
        elif abs(chg_rotation-90.) < ang_close:
            self.snap_shot()
            if not self.add_new_block(RoadTurn, modifier="left"):
                return False
        elif abs(chg_rotation-180.) < ang_close:
            return self.backup_adj()    # Backup if possible

        elif abs(chg_rotation-270.) < ang_close:
            self.snap_shot()
            if not self.add_new_block(RoadTurn, modifier="right"):
                return False
        else:
            SlTrace.lg("track_adjust_key %s not yet supported" % key)
            return False
        return True


    def backup_adj(self):
        """ Backup track adjustment - replace block with back_block link, removing block
        :returns: True iff successful
        """
        back_road = self.block.back_road
        if back_road is None:
            SlTrace.lg("Can't backup")
            return False
        self.race_track.remove_entry(self.block)
        back_road.front_road = None     # Remove forward link
        return self.show_track_adjustments(back_road)
        

    def add_new_block(self, road_type=None, modifier=None, over_road_ok=False):
        """ Add new block if possible doesn't go over edge or get so close
        that another road operation is not possible
        :road_type:  road type(class)
        :modifier: left/right
        :over_road_ok:  ok to go over other road segment
        """
        race_track = self.race_track
        self.remove_markers()       # Avoid colliding with markers
        if not self.road_room_check(self.block, road_type=road_type, modifier=modifier,
                               over_road_ok=over_road_ok):
            return False
        
        new_block = self.block.front_add_type(road_type, modifier=modifier)
        self.race_track.add_entry(new_block)
        self.block.link_roads(new_block)
        nbc = new_block.get_coords()
        x,y = nbc[0],nbc[1]
        SlTrace.lg("new block: %s at x=%.2f y=%.2f" % (new_block, x, y))
        new_front_pt = new_block.get_front_addon_position()
        if not self.is_pos_in_track(new_front_pt):
            self.beep()
            SlTrace.lg("Next block won't fit in track")
            self.race_track.remove_entry(new_block)
            return False
        self.remove_markers()
        self.show_track_adjustments(new_block)
        self.race_track.add_to_group(new_block)
        return True 


    def beep(self):
        self.race_track.beep()


    def is_pos_in_track(self, position):
        return self.race_track.is_pos_in_track(position)
        
    
    def track_adjust(self, ck_block, x=None, y=None):
        """ Adjust track, if possible
        :ck_block:    adjustment block
        :x:        current coordinates of mouse
        :y:
        """
        x_threshold = 1.5       # Strait
        y_threshold = .1        # Strait
        block = self.block
        new_internal_pt = block.get_internal_point([x,y])
        SlTrace.lg("track_adjust internal pt: %s" % new_internal_pt)
        block_coords = block.get_coords()
        SlTrace.lg("track_adjust block: %s coords: %s" % (block, block_coords))
        initial_pt = self.block.get_internal_point(self.initial_coords)
        chg_pt = new_internal_pt - self.initial_pt
        SlTrace.lg("\nchg_pt: %s new:%s, x=%.2f, y=%.2f start:%s %s" %
                    (chg_pt, new_internal_pt, x, y, initial_pt, self.initial_coords))
        new_block = None            # Set if adding a new block
        if abs(chg_pt.y) > abs(chg_pt.x):
            if abs(chg_pt.y) >= y_threshold:
                SlTrace.lg("track_adjust: Adding RoadStrait")
                new_block = self.block.front_add_type(RoadStrait)
                SlTrace.lg("new block: %s at x=%.2f y=%.2f" % (new_block, x, y))
            else:
                ck_block.set_position(ck_block.get_relative_point(chg_pt))
                SlTrace.lg("just moving: %s at x=%.2f y=%.2f" % (ck_block, x, y))
        else:
            if abs(chg_pt.x) >= x_threshold:
                SlTrace.lg("track_adjust: Adding RoadTurn")
                if chg_pt.x <= 0.:
                    modifier = "left"
                else:
                    modifier = "right"
                new_block = self.block.front_add_type(RoadTurn, modifier=modifier)
                SlTrace.lg("new block: %s at x=%.2f y=%.2f" % (new_block, x, y))
            else:
                ck_block.set_position(ck_block.get_relative_point(chg_pt))    
        if new_block is not None:
            self.remove_markers()
            self.race_track.add_entry(new_block)
            self.show_track_adjustments(new_block)
            return True
        
        return False


    def road_room_check(self, road, road_type=None, modifier=None, over_road_ok=False):
        """ Check if adding a new block if possible doesn't go over edge or get so close
        that another road operation is not possible
        :road: our road block to be extended
        :road_type:  road type(class)
        :modifier: left/right
        :over_road_ok:  ok to go over other road segment
        """
        return self.race_track.road_room_check(road, road_type=road_type, modifier=modifier,
                                               over_road_ok=over_road_ok)
            
    def remove_markers(self):
        """ Remove adjustment markers' blocks/display
        """
        if self.adj_block is not None:
            self.adj_block.remove_display_objects()    
            self.race_track.remove_entry(self.adj_block)
            self.adj_block = None
        for block in self.addition_blocks:
            self.race_track.remove_entry(block)
        self.addition_blocks = []    
        for block in self.shifting_blocks:
            self.race_track.remove_entry(block)
        self.shifting_blocks = []    
        for block in self.undo_blocks:
            self.race_track.remove_entry(block)


    def show_track_adjustments(self, block): 
        """ Display distinctly track building control
        Esentially the control will appear as a block over
        the existing selected block.
        The operations are:
          1. Mouse down motion in the direction of the block
          will create a new strait block at the head of the
          selected block when the motion is a sizable fraction of the
          block's length
             a. new block will be created
             b. the cursor will be placed toward the
                front ot the new block
             c. A new overlaying adjustment block will
                be created
         2. Mouse down motion sideways to the ending direction
        of the block will create a new turning block in the
        direction of the sideways motion.
        
        set/reset race_track.track_adjustment
        :block: around which the selections are placed - close to their possible placement
        :returns: True iff OK
        """
        race_track = self.race_track
        if race_track.track_adjustment is not None:
            self.remove_markers()
        self.block = block              # Make new focus
        SlTrace.lg("\nshow_track_adjustments: block: %s coords:%s" % (block, block.get_coords()))
        initial_coords = block.get_center_coords()
        block_coords = block.get_coords()
        x_fudge = (block_coords[6]-block_coords[0])*1.5           # HACK adjusment
        initial_coords[0] += int(x_fudge)                            # HACK adjusment
        y_fudge = (block_coords[3]-block_coords[1])*0
        ###initial_coords[1] += int(y_fudge)                                # HACK adjustment
        start_coords = initial_coords
        self.initial_coords = self.start_coords = start_coords
        SlTrace.lg("start_coords: %s" % start_coords)
        SlTrace.lg("awaiting mouse down at %s" % start_coords)
        race_track.move_cursor(x=start_coords[0], y=start_coords[1])
        self.change_key_state(race_track.key_state) 
        race_track.track_adjustment = self      # Mark it so race track can see
        return True


    def change_key_state(self, key_state=KeyState.EXTEND_ROAD):
        """ Change key state / view
        :key_state:  new state
        """
        race_track = self.race_track
        self.remove_markers()
        block = self.block
        if race_track.key_state == KeyState.EXTEND_ROAD or race_track.key_state == KeyState.ADD_ROAD:
            adj_block = race_track.front_place_type(block, BlockArrow, grouped=False, width=block.get_width(),
                                                    height=block.get_length(),
                                                    color="pink")
        else:
            adj_block = race_track.front_place_type(block, BlockCross, grouped=False, width=block.get_width(),
                                                    height=block.get_length(),
                                                    color="orange")
        self.adj_block = adj_block
        block.display()
        adj_block.display()
        self.adj_block = adj_block
        


    def snap_shot(self, save=True):
        """ snap shot of race_track state to
        shallow info only just delete, select info preserved
        """
        self.race_track.snap_shot()
        
        
 

    def undo_cmd(self):
        return self.race_track.undo_cmd()
    
    
    def redo_cmd(self):
        return self.race_track.redo_cmd()
        