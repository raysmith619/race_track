#race_way.py 14May2025  crs pop off race_track.py
""" 
Top level of race way
Primarily to facilitate snapshot of race track
"""
import copy


from select_trace import SlTrace
from select_error import SelectError

from race_track import RaceTrack
from block_block import BlockBlock

class RaceWay(BlockBlock):
    """
    Race track 
    which can be used to construct a track plus road, track bins
    """
            
    def __init__(self,
                mw=None,
                bin_thick=50,           # Bin thickness in pixels, 0 => no bins
                **kwargs
                ):
        """ Setup track plus bin
        :bin_thick: bin thickness, in_pixels 0 => no bins
        :update_interval: display update interval (sec)
        if container is None:
            set width, height to pixel(absolute)
        """
        self.snap_shot_undo_stack = []
        self.snap_shot_redo_stack = []
        self.race_track = None      # define to avoid undef
        self.race_track = RaceTrack(self,
                mw=mw,
                bin_thick=bin_thick,   # Bin thickness in pixels, 0 => no bins
                **kwargs)
        if self.race_track is not None:
           self.race_track.race_way = self  # Can't set during __init__
            
        self.road_track = self.race_track.road_track


    """ race_track snapshot support
    """
    
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

    def snap_shot(self, save=True):
        """ snap shot of race_track state
        implement simple do/undo
        :save: if True, save snap shot on undo stack
        :returns: snap shot of state
        """
        snap = copy.deepcopy(self.race_track)
        if save:
            self.snap_shot_undo_stack.append(snap)
        return snap
        
    def snap_shot_restore(self, snap):
        """ Restore state from snap shot
        :snap: snap shot of state
        """
        if snap is not None:
            self.race_track.__dict__.update(snap.__dict__)

    
    """ 
    Links to race_track
    """
    def add_entry(self, entries, grouped=True):
        """ Add cas/roads to track
        :entries: car/roads to add
        :grouped: Add to current group
        """
        self.race_track.add_entry(entries, grouped=grouped)


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
        return self.race_track.add_to_track(block,
                        select=select, display=display,
                        x=x, y=y, **kwargs)        

    
    def display(self):
        """ Display track
        """
        self.race_track.display()

    def enable_window_resize(self):
        """ Enable manual resizing after setup
        """
        self.race_track.enable_window_resize()
        
            
    def pos_change_control_proc(self, change):
        """ Part position change control processor
        :change: identifier (see PositionWindow)
        """
        self.race_track.pos_change_control_proc(change=change)

    def race_control_proc(self, command):
        """ Race control commands
        """
        self.race_track.race_control_proc(command=command)

    def get_road_bin(self):
        return self.race_track.get_road_bin()

    def save_bin_selection(self, block):
        """ Save selection to drive next car track click - add duplicate to track
        :block: block to duplicate on track
        """
        self.race_track.save_bin_selection(block)

    def get_car_bin(self):
        return self.race_track.get_car_bin()
                    
if __name__ == "__main__":
    import os
    import sys

    from homcoord import *
    
    from tkinter import *    
    import argparse
    
    from road_block import RoadBlock
    from road_turn import RoadTurn
    from block_arc import BlockArc


    from road_block import RoadBlock
    from road_track import RoadTrack
    from road_straight import RoadStraight
    from road_turn import RoadTurn
    from road_panel import RoadPanel
    from car_block import CarBlock
    from car_simple import CarSimple
    from block_block import BlockBlock
    from block_mouse import BlockMouse
    from car_race import CarRace
    from track_adjustment import TrackAdjustment, KeyState
    from block_commands import BlockCommands, car


    SlTrace.setFlags("short_points")
    
    bin_thick = None        # Use default, Note: 0 ==> no bins
    width = 600     # Window width
    height = width  # Window height
    rotation = None # No rotation
    pos_x = None
    pos_y = None
    parser = argparse.ArgumentParser()
    dispall = False      # Display every change
    
    parser.add_argument('--bin_thick=', '--bt', type=int, dest='bin_thick', default=bin_thick)
    parser.add_argument('--width=', type=int, dest='width', default=width)
    parser.add_argument('--height=', type=int, dest='height', default=height)
    parser.add_argument('--pos_x=', type=float, dest='pos_x', default=pos_x)
    parser.add_argument('--pos_y=', type=float, dest='pos_y', default=pos_y)
    parser.add_argument('--rotation=', type=float, dest='rotation', default=rotation)
    args = parser.parse_args()             # or die "Illegal options"
    
    bin_thick = args.bin_thick
    width = args.width
    height = args.height
    pos_x = args.pos_x
    pos_y = args.pos_y
    rotation = args.rotation
    
    SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
    SlTrace.lg("args: %s\n" % args)
    
            
    frame = Frame(width=width, height=height, bg="", colormap="new")
    frame.pack(fill=BOTH, expand=YES)
    canvas = Canvas(frame, width=width, height=height)
    canvas.pack(fill=BOTH, expand=YES)   
    th_width = 1.
    th_height = 1.
    position = None
    if pos_x is not None or pos_y is not None:
        if pos_x is None:
            pos_x = 0.
        if pos_y is None:
            pos_y = 0.
        position = Pt(pos_x, pos_y)
        
    tR = RaceWay(canvas=canvas, width=th_width, height=th_height,
                   bin_thick=bin_thick,
                   position=position,
                   cv_width=width, cv_height=height,
                   rotation=rotation)
    
    """ ISSUE
        Why does rd.front_add_type(...) give erroneous positioning when
        rd = RoadStraight(track=tR.road_track, position=Pt(.5,.5))
        ???
    """
    rd0 = RoadStraight(track=tR.road_track, position=Pt(.5,.5))
    pos_coords = [300,300]
    rd = tR.add_to_track(rd0,x=pos_coords[0], y=pos_coords[1],
                            select=False, display=False)
    tR.add_entry(rd)
    tR.display()
    rd2 = rd.front_add_type(RoadStraight)
    tR.add_entry(rd2)
    tR.display()
    rd2a = rd2.front_add_type(RoadStraight)
    tR.add_entry(rd2a)
    tR.display()
    rd3 = rd2a.front_add_type(RoadTurn, modifier="right")
    tR.add_entry(rd3)
    tR.display()
    rd4 = rd3.front_add_type(RoadStraight)
    tR.display()
    tR.add_entry(rd4)
    tR.display()
    tR.enable_window_resize()
    tR.display()

    mainloop()