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
from road_block import RoadBlock,SurfaceType
from road_strait import RoadStrait
from road_turn import RoadTurn
from road_panel import RoadPanel
from block_mouse import BlockMouse
from docutils.nodes import sidebar
from dist.hello.unicodedata import bidirectional
from numpy import block
from _operator import pos


class SnapShot:
    """ Snap shot info to provide undo info
    """
    def __init__(self):
        self.roads = {}
        self.selects_list = []    
        
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
        self.car_bin = BlockPanel(tag="car_bin",
                             container=self, position=car_bin_position,
                             width=car_bin_width, height=car_bin_height,
                             background="lightpink")
         
        self.road_bin = RoadPanel(container=self, position=road_bin_position,
                             width=road_bin_width, height=road_bin_height,
                             background="lightgray")
        SlTrace.lg("road_bin pts: %s" % self.road_bin.get_absolute_points())
        
        self.road_track = RoadTrack(container=self, position=track_position,
                               width=track_width, height=track_height,
                               background="lightgreen")
        self.set_reset()        # Set reset state - can be changed
        self.set_snap_stack = []


    def add_track_block(self, block):
        """ Add displayed race track block, including on track, on bins
        :block: block to be added
        """
        
        
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


    def get_road_track(self):
        return self.road_track

    def get_road(self, road_id):
        """ Get road on track
        """
        road_track = self.get_road_track()
        if road_track is None:
            return
        
        return road_track.get_road(road_id)
        
        
        

    def get_road_at(self, x=None, y=None, all=False):
        """ Return road at canvas coordinates
        :x: x canvas coordinate
        :y: y canvas coordinate
        :all: if True return list of all roads which contain this coordinate
              if False just first block found which contains this coordinate
        """
        road_track = self.get_road_track()
        if road_track is None:
            return None             # No track yet
        
        roads = road_track.roads
        roads_found = []
        for road in roads.values():
            if road.is_at(x=x, y=y):
                roads_found.append(road)
                if not all:
                    break
        if all:
            return roads_found
        
        if roads_found:
            return roads_found[0]
        
        return None
    
    

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
        
        
    def mouse_down (self, event):
        mouse_info = self.get_info(event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        if SlTrace.trace("mouse_click"):
            SlTrace.lg("Clicked at x=%d y=%d shift_down=%s" % (x,y, self.is_shift_down()))
        if self.is_in_track(x,y):
            self.snap_shot()
            if self.is_shift_down():                # Shift is grouping control
                road_block = self.get_road_at(x,y)
                if road_block is not None:
                    if road_block.is_selected():
                        self.clear_selected(road_block.id)
                    else:
                        self.set_selected(road_block.id, x_coord=x,
                                           y_coord=y,keep_old=True)
                    return
                else:
                    SlTrace.lg("No road found at x=%d  y=%d" % (x,y))
                return
            
            if self.is_bin_selected():
                block = self.bin_selection
                self.add_to_track(block,x=x, y=y)
                return
            
            road_block = self.get_road_at(x,y)
            if road_block is not None:
                self.set_selected(road_block)
            else:
                self.clear_selected()       # Clear all
                
            return                  # End of in track operation
        
        if self.is_in_road_bin(x,y):    
            SlTrace.lg("In road bin")
            mouse_block = self.get_event_block(types=(RoadStrait,RoadTurn))
            if mouse_block is not None:
                SlTrace.lg("Clicked block[%s]:%s at x=%d y=%d" % (mouse_block.get_tag_list(), mouse_block, x,y))
                self.save_bin_selection(mouse_block)
                self.set_selected(mouse_block.id)
                return
            
            self.clear_bin_selection()
            return
        

    def clear_bin_selection(self):
        """ clear selection 
        """
        if self.bin_selected and self.bin_selection is not None:
            self.clear_selected(self.bin_selection.id)
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
    
    
    def is_in_road_bin(self, x=None,y=None):
        """ Check if point (canvas coordinates) is in road bin
        :x,y: x,y canvas coordinates
        """
        bin = self.get_road_bin()
        if bin is None:
            return None
        
        return bin.is_at(x=x, y=y)
    
    
    def is_in_car_bin(self, x=None,y=None):
        """ Check if point (canvas coordinates) is in car bin
        :x,y: x,y canvas coordinates
        """
        bin = self.get_car_bin()
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
        mouse_block = self.get_event_block(types=(RoadStrait,RoadTurn), event=event)
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
           


    def mouse_down_motion_car_bin(self, mouse_info=None, mouse_block=None):
        x,y = mouse_info.x_coord, mouse_info.y_coord
        SlTrace.lg("\nmotion_car_bin: %s at xy(%d,%d)" % (mouse_block, x,y))
        if mouse_block.state == "selected":
            selected = self.get_selected(mouse_block)
            if selected is not None:
                SlTrace.lg("mouse_block %s is selected" % mouse_block)
            else:
                SlTrace.lg("mouse_block %s is not selected - IGNORED\n" % mouse_block)
                return
            
            '''new_block = mouse_block.dup()# Hack because we don't move the block
            new_block.state = "new"
            delta_x = x - selected.x_coord_prev 
            delta_y = y - selected.y_coord_prev
            new_selected = self.set_selected(new_block.id, x_coord=x, y_coord=y)
            new_block.drag_block(delta_x=delta_x, delta_y=delta_y, canvas_coord=True)
            ###new_block.display()
            SlTrace.lg("new_block(%s)[%s] dragged to x,y=%d,%d" %
                        (new_block, new_block.get_tag_list(), x, y))
            new_selected.x_coord_prev = x 
            new_selected.y_coord_prev = y
            mouse_block.state = "old"
            ###self.clear_selected(mouse_block)
            new_block.display()
            '''
            mouse_block.state = "new"
            mouse_block.display()
           
            return
            
        elif mouse_block.state == "new":
            SlTrace.lg("mouse_block %s now new state" % mouse_block)
            selected = self.get_selected(mouse_block)
            SlTrace.lg("is still selected") 
            if selected is None:
                SlTrace.lg("mouse_down_motion_car_bin %s not selected" % mouse_block)
                return
        
            mouse_info = self.get_mouse_info()
            SlTrace.lg("%s selected(%s) to x,y=%d,%d" % (mouse_block, selected.block, x, y))
       
            if selected.x_coord_prev is None:
                SlTrace.lg("%s None x_coord_prev selected(%s) to x,y=%d,%d" % (mouse_block, selected.block, x, y))
                return
            
            block = selected.block       
            delta_x = x - mouse_info.x_coord_prev 
            delta_y = y - mouse_info.y_coord_prev
            ###block.drag_block(delta_x=delta_x, delta_y=delta_y, canvas_coord=True)
            ###SlTrace.lg("Dragged %s[%s] delta_xy=(%d,%d) new_xy=(%d,%d)" %
            ###            (block, block.get_tag_list(), delta_x,delta_y, x,y), "dragged")
            ###block.state = "moved"
            ###self.set_selected(block.id, x_coord=x, y_coord=y)
            ###block.display()
            ###SlTrace.lg("selected new in road_bin")
            ###selected.x_coord_prev = x 
            ###selected.y_coord_prev = y 
            ###block.display()
            # HACK - transform (for now just create new) into entry on track
            self.move_to_track(block, bin_x=x, bin_y=y)
            mouse_info.x_coord
        else:
            SlTrace.lg("mouse_down_motion_car_bin unrecognize state: %s" % mouse_block)


    def mouse3_down(self, event=None):
        """ Implement right shift operations
        :event: current event if one
        """
        mouse_info = self.get_info(mouse_no=3, event=event)
        x,y = mouse_info.x_coord, mouse_info.y_coord
        SlTrace.lg("mouse3 down at x=%d y=%d" % (x,y), "motion_to")
        if SlTrace.trace("mouse_right_info"):
            roads = self.get_road_at(x=x, y=y, all=True)
            if len(roads) == 0:
                SlTrace.lg("No roads at xy(%d,%d)" % (x,y))
                return
            
            if len(roads) > 1:
                SlTrace.lg("%d roads(%s) found at xy(%d,%d)" %
                           (len(roads), roads, x,y))
            for road in roads:
                SlTrace.lg("%s rot: %.0f pos: %s  front add: rot: %.0f pos: %s" %
                           (road, road.get_rotation(), road.abs_pos(),
                           road.get_front_addon_rotation(), road.abs_front_pos()))
                
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


    def add_to_track(self, block, x=None, y=None):
        """ Add duplicate of object in bin(block) to track att current location
        :block: object to move
        :x: x bin position in pixels
        :y: y bin position in pixels
        """
        road_length = self.get_road_length()
        road_width = self.get_road_width()
        if issubclass(type(block),RoadTurn):
            road_length = road_width
        new_block = block.dup(origin="road_track", container=self, rotation=0.,
                               width=road_width, height=road_length, radius=road_width)
        new_block.set_position(position=Pt(x,y), canvas_coord=True)
        self.add_road(new_block)
        self.set_selected(new_block.id, keep_old=True)
        new_block.display()             # Hack to change tag        

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

        self.add_road(track_block)
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
        for road in list(road_track.roads.values()):
            self.delete_road(road.id)            
        for road in snap.roads.values():
            self.add_road(road)
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
        elif change == "back_add_strait":
            self.back_add_type(RoadStrait)
        elif change == "back_add_left_turn":
            self.back_add_type(RoadTurn, "left")
        elif change == "back_add_right_turn":
            self.back_add_type(RoadTurn, "right")
        elif change == "select_none":
            for block in selected_blocks:
                self.clear_selected(block.id)
                block.display()
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
            for road in self.get_selected_blocks(origin="road_track"):
                self.delete_road(road.id)
        elif change == "delete_all":
            roads = list(self.road_track.roads.values())
            for road in roads:
                road_id = road.id
                self.delete_road(road_id)
        else:
            SlTrace.lg("position_change_control_proc: change(%s) not yet implemented" % change)
            return False        # Unsuccessful

        return True                 # Successful


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
    
    def delete_road(self, road_id):
        """ Delete road from race_track
        :road_id: road's block id
        """
        road_track = self.get_road_track()
        if road_track is None:
            return          # No track
        
        if SlTrace.trace("delete"):
            SlTrace.lg("delete road: %d" % road_id)
        self.clear_selected_block(road_id)
        road = self.get_road(road_id)
        if road is not None:
            road.remove_display_objects(do_comps=True)
            road_track.remove_road(road_id)
        
    
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
        self.add_road(new_block)
        SlTrace.lg("back_add_type: new_block:%s" % new_block, "add_block")
        SlTrace.lg("back_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        new_block.move_to(position=add_pos)
        SlTrace.lg("back_add_type: moved new_block:%s" % new_block, "add_block")
        SlTrace.lg("back_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        ###self.set_selected(new_block, keep_old=True)
        self.set_selected(new_block.id, keep_old=True)
        canvas = self.get_canvas()
        new_block.display()
        
    
    def front_add_type(self, new_type=None, modifier=None):
        """ Add RoadStrait to front end(top end of most recently selected)
            TBD: Possibly changed to determine end of physically connected string
        """
        sel_list = self.get_selected_blocks()
        if not sel_list:
            return      # None selected
        
        SlTrace.lg("\nfront_add_type: new_type:%s modifier:%s" %
                   (new_type, modifier), "add_block")
        front_block = sel_list[-1]
        SlTrace.lg("front_add_type: front_block:%s" % front_block, "add_block")
        SlTrace.lg("front_add_type: points:%s" % front_block.get_absolute_points(), "add_block")
        add_pos = front_block.get_front_addon_position()
        add_rot = front_block.get_front_addon_rotation()
        if SlTrace.trace("add_block"):
            abs_pos = self.get_absolute_point(add_pos)
            SlTrace.lg("front_add_type: front rot:%.0f pos:%s(%s) rot:%.0f" %
                        (front_block.rotation, add_pos, abs_pos, add_rot))
        new_block = front_block.new_type(new_type, modifier)
        if add_rot != new_block.get_rotation():
            new_block.set_rotation(add_rot)   # Small optimization
        self.add_road(new_block)
        SlTrace.lg("front_add_type: new_block:%s" % new_block, "add_block")
        SlTrace.lg("front_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        new_block.move_to(position=add_pos)
        SlTrace.lg("front_add_type: moved new_block:%s" % new_block, "add_block")
        SlTrace.lg("front_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        ###self.set_selected(new_block, keep_old=True)
        self.set_selected(new_block.id, keep_old=True)
        canvas = self.get_canvas()
        new_block.display()

    def add_road(self, road):
        """ Add road segment to track
        :road: road to add
        """
        self.road_track.add_road(road)
        
        
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