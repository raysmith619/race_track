from tkinter import *
from homcoord import *
from enum import Enum

from select_trace import SlTrace
from select_error import SelectError

from block_arrow import BlockArrow
from block_cross import BlockCross
from block_pointer import BlockPointer, AdjChoice
from road_block import RoadBlock, SurfaceType
from road_straight import RoadStraight
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
        self.prev_adjust_x = -1                         # HACK - TO BE REMOVED ???
        self.prev_adjust_y = -1
    
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


    def mouse_down(self, x=None, y=None):
        """ Process mouse_down for track adjustment
        :x: x coord
        :y: y coord
        """
        adj_block = self.adj_block
        if adj_block is None:
            return False
        
        if not adj_block.is_at(x,y):
            return False
       
        choice = adj_block.highlight(x,y, display=False)       # Display after update
        if choice == AdjChoice.FORWARD:
            chg_rotation = 0.
        elif choice == AdjChoice.LEFT:
            chg_rotation = 90.
        elif choice == AdjChoice.BACKWARD:
            chg_rotation = 180.
        elif choice == AdjChoice.RIGHT:
            chg_rotation = 270.     
        else:
            raise SelectError("Unsupported adjChoice:%s" % choice)
        return self.change_rotation(chg_rotation)
    
    
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
        return self.change_rotation(chg_rotation)
    
    
    def change_rotation(self, chg_rotation):
        """ Change rotation adding appropriate road
        :chg_rotation: angle of change
        """

        SlTrace.lg("chg_rotation: %.1f" % chg_rotation)
        chg_rotation = chg_rotation % 360.
        ang_close = .1
        
        if abs(chg_rotation) < ang_close:   # 0 
            self.snap_shot()
            SlTrace.lg("track_adjust: Adding RoadStraight")
            if self.add_new_block(RoadStraight):
                return True
        elif abs(chg_rotation-90.) < ang_close:
            self.snap_shot()
            if self.add_new_block(RoadTurn, modifier="left"):
                return True
        elif abs(chg_rotation-180.) < ang_close:
            return self.backup_adj()    # Backup if possible

        elif abs(chg_rotation-270.) < ang_close:
            self.snap_shot()
            if self.add_new_block(RoadTurn, modifier="right"):
                return True
        else:
            SlTrace.lg("change_rotation %.2f not yet supported" % chg_rotation)
            self.beep()
            return False
        
        SlTrace.lg("Can't go in %.2f deg" % chg_rotation)
        self.beep()
        if self.block is None:
            raise SelectError("No block to go back to")
        self.show_track_adjustments(self.block)
        return False


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
        self.remove_markers(keep_adj=True)       # Avoid colliding with markers
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
        self.remove_markers(keep_adj=True)
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
        if ck_block.is_at(x=x, y=y):
            self.highlight(ck_block, x=x, y=y)
            return True
        
        return False
    
    def highlight(self, ck_block, x=None,  y=None):
        """ Hilight adjustment block
        :ck_block: adjustment block
        :x: x coordinate
        :y: y coordinate
        """
        if ck_block is None:
            return False
        
        ck_block.highlight(x=x, y=y)
        if ck_block.comps:
            for comp in ck_block.comps:
                self.addition_blocks.append(comp)
        return True
    

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
            
    def remove_markers(self, keep_adj=False):
        """ Remove adjustment markers' blocks/display
        :keep_adj: keep main reference
        """
        race_track = self.race_track
        if self.adj_block is not None:
            ###self.adj_block.remove_display_objects()    
            race_track.remove_entry(self.adj_block)
            self.adj_block = None
        for block in self.addition_blocks:
            race_track.remove_entry(block)
        self.addition_blocks = []    
        for block in self.shifting_blocks:
            race_track.remove_entry(block)
        self.shifting_blocks = []    
        for block in self.undo_blocks:
            race_track.remove_entry(block)
        if not keep_adj:
            race_track.track_adjustment = None

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
        self.change_key_state(race_track.key_state)
        adj_coords = self.adj_block.get_adj_coords(AdjChoice.FORWARD) 
        race_track.move_cursor(x=adj_coords[0], y=adj_coords[1])
        self.highlight(self.adj_block, x=adj_coords[0], y=adj_coords[1])
        race_track.track_adjustment = self      # Mark it so race track can see
        return True


    def change_key_state(self, key_state=KeyState.EXTEND_ROAD):
        """ Change key state / view
        :key_state:  new state
        """
        race_track = self.race_track
        self.remove_markers(keep_adj=True)
        block = self.block
        if race_track.key_state == KeyState.EXTEND_ROAD or race_track.key_state == KeyState.ADD_ROAD:
            adj_block = race_track.front_place_type(block, BlockPointer, grouped=False, width=block.get_width(),
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
        