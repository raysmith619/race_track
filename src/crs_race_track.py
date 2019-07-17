# race_track.py        
"""
Basis of a race track
Includes RoadTrack with road and car bins
"""
import os
import sys
from tkinter import *    
import argparse
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError
from block_window import BlockWindow
from road_track import RoadTrack
from block_panel import BlockPanel
from block_block import BlockBlock,BlockType
from block_polygon import BlockPolygon
from road_block import RoadBlock,SurfaceType
from road_strait import RoadStrait
from race_track import RaceTrack
from road_bin_setup import RoadBinSetup
from road_track_setup import RoadTrackSetup
from road_block import RoadBlock
from road_turn import RoadTurn
from block_arc import BlockArc
from position_window import PositionWindow

SlTrace.setFlags("short_points,starter_track,down"
                 + ",add_block,mouse_right_info")

width = 600     # Window width
height = width  # Window height
rotation = None # No rotation
pos_x = None
pos_y = None
parser = argparse.ArgumentParser()
dispall = False      # Display every change
starter_track = True

parser.add_argument('--width=', type=int, dest='width', default=width)
parser.add_argument('--height=', type=int, dest='height', default=height)
parser.add_argument('--pos_x=', type=float, dest='pos_x', default=pos_x)
parser.add_argument('--pos_y=', type=float, dest='pos_y', default=pos_y)
parser.add_argument('--rotation=', type=float, dest='rotation', default=rotation)
parser.add_argument('--starter_track', '-st', type=float, dest='starter_track', default=starter_track)
args = parser.parse_args()             # or die "Illegal options"

width = args.width
height = args.height
pos_x = args.pos_x
pos_y = args.pos_y
rotation = args.rotation

SlTrace.lg("%s %s\n" % (os.path.basename(sys.argv[0]), " ".join(sys.argv[1:])))
SlTrace.lg("args: %s\n" % args)

# Program exit control
def pgm_exit():
    ###ActiveCheck.clear_active()  # Disable activities
    quit()
    SlTrace.lg("Properties File: %s"% SlTrace.getPropPath())
    SlTrace.lg("Log File: %s"% SlTrace.getLogPath())
    sys.exit(0)

def play_exit():
    """ End playing
    Called from Window control
    """
    ###ActiveCheck.clear_active()  # Disable activities
    pgm_exit()


mw = Tk()        
app = BlockWindow(master=mw,
                title="My Race Track",
                pgmExit=play_exit,
                cmd_proc=True,
                cmd_file=None,
                arrange_selection=False,
                game_control=None
                )
frame = Frame(app, width=width, height=height, bg="", colormap="new")
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

tR = RaceTrack(mw=mw, canvas=canvas, width=th_width, height=th_height,
               position=position,
               cv_width=width, cv_height=height,
               rotation=rotation)
tR.display()
pos_ctl = PositionWindow("Part Positioning",
                         change_control_proc=tR.pos_change_control_proc)    

if starter_track:
    road_track = tR.get_road_track()
    RoadTrackSetup(road_track)

road_bin = tR.get_road_bin()
RoadBinSetup(road_bin)
tR.set_reset()


###RoadBinSetup(road_track)
tR.display()


mainloop()