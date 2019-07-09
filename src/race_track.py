# race_track.py        
"""
Basis of a race track
Includes RoadTrack with road and car bins
"""
from tkinter import *
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from road_track import RoadTrack
from block_panel import BlockPanel
from block_block import BlockBlock,BlockType
from block_polygon import BlockPolygon
from road_block import RoadBlock,SurfaceType
from road_strait import RoadStrait
from road_turn import RoadTurn
from road_panel import RoadPanel
from block_mouse import BlockMouse
from docutils.nodes import sidebar
from dist.hello.unicodedata import bidirectional
from numpy import block

class SelectInfo:
    """ Selected block information
    Used to provide operation on selected objects
    """
    
    def __init__(self, block=None, x_coord=None, y_coord=None, x_coord_prev=None,  y_coord_prev=None):
        if block is None:
            raise SelectError("SelectInfo when block is None")
        
        if x_coord is None:
            raise SelectError("SelectInfo when x_coord is None")
        
        self.x_coord = x_coord
        self.y_coord = y_coord
        if x_coord_prev is None:
            x_coord_prev = x_coord
        self.x_coord_prev = x_coord_prev
        if y_coord_prev is None:
            y_coord_prev = y_coord
        self.y_coord_prev = y_coord_prev
        self.block = block
        
    def __repr__(self):
        str_str = "%s" % self.block
        return str_str
        
    def __str__(self):
        str_str = "%s" % block
        return str_str
    
        
class RaceTrack(RoadTrack, BlockMouse):
    """
    Race track 
    which can be used to construct a track plus road, track bins
    """
            
    def __init__(self,
                bin_thick=50,           # Bin thickness in pixels
                **kwargs
                ):
        """ Setup track plus bin
        if container is None:
            set width, height to pixel(absolute)
        """
        self.selects = {}               # ids of selected
        self.motion_bind_id = None
        self.car_bin = None             # Set if present
        self.road_bin = None
        self.road_track = None
        self.event_block = None         # Set to get very next event
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
        if len(item_tags) == 0:
            SlTrace.lg("get_event_block - no CURRENT", "get_event_block")
            if event is not None:
                SlTrace.lg("Check for item close", "get_event_block")
                item_tag = None
                item = canvas.find_closest(event.x, event.y)
                item_id = item[0]
                for bid in self.selects:
                    selected_info = self.selects[bid]
                    selected_block = selected_info.block
                    canvas_tags = selected_block.get_canvas_tags()
                    if item_id in canvas_tags:
                        item_tag = item_id
                        if SlTrace.trace("motion"): SlTrace.lg("Found close canvas_tag: %s block %s "
                                    % (item_tag,selected_block))
                        break
                if item_tag is None:
                    return None
        else:
            item_tag = item_tags[0]
            SlTrace.lg("get_event_block: tag:%s" % item_tag)
        if item_tag is None:
            return None
        
        if not item_tag in BlockBlock.tagged_blocks:
            return None
        
        cur_block = BlockBlock.tagged_blocks[item_tag]
        SlTrace.lg("tag=%s id=%d" % (item_tag, cur_block.id), "tagged block")
        
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
    

    def mouse_down (self, event):
        mouse_block = self.get_event_block(types=(RoadStrait,RoadTurn))
        if mouse_block is not None:
            x,y = event.x, event.y
            SlTrace.lg("Clicked block[%s]:%s at x=%d y=%d" % (mouse_block.get_tag_list(), mouse_block, x,y))
            if mouse_block.origin == "road_bin":
                SlTrace.lg("In road bin")
                self.move_to_track(mouse_block, bin_x=x, bin_y=y)
                return
            
            elif mouse_block.origin == "car_bin":
                SlTrace.lg("In car bin")
            elif mouse_block.origin == "road_track":
                SlTrace.lg("In car track")
            else:
                SlTrace.lg("Unrecognized origin: %s" % mouse_block.origin)
            mouse_block.state = "selected"
            self.set_selected(mouse_block, x_coord=x, y_coord=y)
            mouse_block.display()
        else:
            self.clear_selected()

        
    def mouse_down_motion (self, event):
        ###cnv.itemconfigure (tk.CURRENT, fill ="blue")
        cnv = event.widget
        x,y = event.x, event.y
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("move to x=%d y=%d" % (x,y), "motion_down")
        mouse_block = self.get_event_block(types=(RoadStrait,RoadTurn), event=event)
        if mouse_block is None:
            return
        
        if mouse_block.origin == "road_bin":
            self.mouse_down_motion_car_bin(event, mouse_block)
            return
        
        elif mouse_block.origin == "car_bin":
            SlTrace.lg("In car bin")
        elif mouse_block.origin == "road_track":
            SlTrace.lg("In car track")
        else:
            SlTrace.lg("Unrecognized origin: %s" % mouse_block.origin)

        # Lump rest here for now
        selected = self.get_selected(mouse_block)
        if selected is None:
            return
        
        block = selected.block
        if block is None:
            raise SelectError("mouse_down_motion when selected.block is None")
        
        x,y = event.x, event.y
        delta_x = x - selected.x_coord_prev 
        delta_y = y - selected.y_coord_prev
        block.drag_block(delta_x=delta_x, delta_y=delta_y, canvas_coord=True)
        SlTrace.lg("Dragged %s %s delta_xy=(%d,%d) new_xy=(%d,%d)" %
                    (block.get_tag_list(), block, delta_x,delta_y, x,y), "dragged")
        block.display()
        selected.x_coord_prev = x 
        selected.y_coord_prev = y 
           


    def mouse_down_motion_car_bin(self, event=None, mouse_block=None):
        x,y = event.x, event.y
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
            new_selected = self.set_selected(new_block, x_coord=x, y_coord=y)
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
        
            SlTrace.lg("%s selected(%s) to x,y=%d,%d" % (mouse_block, selected.block, x, y))
       
            if selected.x_coord_prev is None:
                SlTrace.lg("%s None x_coord_prev selected(%s) to x,y=%d,%d" % (mouse_block, selected.block, x, y))
                return
            
            block = selected.block       
            delta_x = x - selected.x_coord_prev 
            delta_y = y - selected.y_coord_prev
            ###block.drag_block(delta_x=delta_x, delta_y=delta_y, canvas_coord=True)
            ###SlTrace.lg("Dragged %s[%s] delta_xy=(%d,%d) new_xy=(%d,%d)" %
            ###            (block, block.get_tag_list(), delta_x,delta_y, x,y), "dragged")
            ###block.state = "moved"
            ###self.set_selected(block, x_coord=x, y_coord=y)
            ###block.display()
            ###SlTrace.lg("selected new in road_bin")
            ###selected.x_coord_prev = x 
            ###selected.y_coord_prev = y 
            ###block.display()
            # HACK - transform (for now just create new) into entry on track
            self.move_to_track(block, bin_x=x, bin_y=y)
        else:
            SlTrace.lg("mouse_down_motion_car_bin unrecognize state: %s" % mouse_block)
            
            
    def mouse_up (self, event):
        self.is_down = False
        ###event.widget.itemconfigure (tk.CURRENT, fill =self.defaultcolor)
        cnv = event.widget
        x,y = cnv.canvasx(event.x), cnv.canvasy(event.y)
        ###got = event.widget.coords (tk.CURRENT, x, y)
        SlTrace.lg("up at x=%d y=%d" % (x,y), "motion")
        SlTrace.lg("up is ignored", "motion")
        return


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
        self.set_selected(track_block, x_coord=track_x, y_coord=track_y)
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
        
        
    def set_selected(self, block, x_coord=None, y_coord=None, x_coord_prev=None,
                     y_coord_prev=None, keep_old=False):
        """ Set/add block to selected blocks
        :block: block to be added
        :x_coord: x canvas coordinate
        :y_coord: y canvas coordinate
        :x_coord_prev: previous x coordinate default: x_coord
        :y_coord_prev: previous y coordinate default: y_coord
        :keep_old: keep old selected default: False (drop previously selected)
        :returns: reference to new selection entry
        """
        if block is None:
            raise SelectError("set_selected with block is None")
        if not keep_old:
            sids = list(self.selects.keys())
            for sid in sids:
                SlTrace.lg("Clearing selected %s" % self.selects[sid].block)
                self.clear_selected(sid)
        selected = SelectInfo(block=block, x_coord=x_coord, y_coord=y_coord,
                              x_coord_prev=x_coord_prev, y_coord_prev=y_coord_prev)
        self.selects[block.id] = selected
        block.selected = True
        SlTrace.lg("set_selected(%s)"  % block)
        return selected
    

    def clear_selected(self, bid=None):
        """ Clear (unset) selected block
            May do some visual stuff in the future
        :bid:  block id, default: clear all selected blocks
        """
        if bid is None:
            sids = list(self.selects.keys())
            for sid in sids:
                self.clear_selected_block(sid)
        else:
            self.clear_selected_block(bid)        


    def clear_selected_block(self, bid):
        """ clear specified block
        :bid: block id to clear selected
        """
        if not bid in self.id_blocks:
            return
                
        block = self.id_blocks[bid]
        comp = block
        while comp is not None:
            blk_id = comp.id
            if blk_id in self.id_blocks and blk_id in self.selects:
                del self.selects[blk_id]
                comp.display()
                
            comp = comp.container


    def get_selected_blocks(self):
        """ Return list of blocks currently selected
        """
        blocks = []
        for select in self.selects.values():
            blocks.append(select.block)
        return blocks
        

    def get_selected(self, block=None):
        """ Get selected info, block if selected, else None
        :block:  block to check.
        """
        if block is None:
            raise SelectError("get_selected: with block is None")

        selected = None
        for sid in self.selects:
            selected = self.selects[sid]
            if selected.block.id == sid:
                break
            
        
        if selected.block is None:
            raise SelectError("selected with None for block")
       
        if selected.x_coord is None:
            SlTrace.lg("selected with None for x_coord")
            cv_width = self.get_cv_width()
            cv_height = self.get_cv_height()
            selected = SelectInfo(block=None, x_coord=cv_width/2, y_coord=cv_height/2)  # HACK
        return selected

           
           
    def is_selected(self, block):
        """ Determine if block is selected
        Is selected if it or any in container tree is in self.selects
        """
        comp = block
        while comp is not None:
            if comp.id in self.selects:
                return True
            comp = comp.container
        return False


    def pos_change_control_proc(self, change):
        """ Part position change control processor
        :change: identifier (see PositionWindow)
        """
        selected_blocks = self.get_selected_blocks()
        len_sels = len(selected_blocks)
        sel_block = None        # Set to block iff only selected
        ltdeg = 90.
        if len_sels == 1:
            sel_block = selected_blocks[0]
        
        if change == "spin_left":
            sel_block.rotate(ltdeg)
        elif change == "spin_right":
            sel_block.rotate(-ltdeg)
        elif change == "flip_up_down" or change == "flip_left_right":
            if isinstance(sel_block, RoadTurn):
                ###sel_block.rotate(180)
                ###sel_block.display()
                sel_block.new_arc(-sel_block.get_arc())

        else:
            SlTrace.lg("position_change_control_proc: change(%s) not yet implemented" % change)
            return
        
        sel_block.display()         # Display after change


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