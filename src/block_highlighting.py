#block_highlight.py 01Jun2025  crs
""" High lighted block
Show interested block by blinking highlight over
existing entry
"""
from select_trace import SlTrace

from homcoord import *
from block_polygon import BlockPolygon
from road_straight import RoadStraight
from road_turn import RoadTurn
from select_error import SelectError

class BlockHighlighting:
    def __init__(self, race_track,
                 on_time_ms=250,
                 off_time_ms=250,
                 line_width=5,
                 color="light gray"):
        """ Setup highlight
        :race_track: race_track reference
        :on_time_ms: display on time in msec
        :off_time_ms: display off time in msec
                reverting to regular display
        :color: highlight display color
        """
        self.race_track = race_track
        self.entry  = None
        self.on_time_ms = on_time_ms
        self.off_time_ms = off_time_ms
        self.display_id = None
        self.color = color
        self.line_width=line_width
        self.tag = None
        self.msg = ""
        
    def check_for_change(self,
                 x=None,
                 y=None):
        """ Establish highlight, check for change
            Make track modifications requested
        """
        race_track = self.race_track
        if x is None:
            x = race_track.move_cursor_x
        self.x = x
        if y is None:
            y = race_track.move_cursor_y
        self.y = y
        self.after_id = None
        entries = race_track.get_entry_at(x=x, y=y, entry_type="road")
        if entries is None:
            entry = None
        elif isinstance(entries, list):
            entry = entries[-1] if len(entries) > 0 else None
        else:
            entry = entries
        if entry is not None and entry != self.entry:
            self.cancel()
            self.entry = entry
        if entry is None:
            if self.entry is not None:
                self.cancel()
            return True
        
        pts = self.entry.get_perimeter_points()
        pts.append(pts[0])   # add first to surround
        coords = self.entry.get_coords(pts) 
        if self.display_id is not None:
            race_track.canvas.delete(self.display_id)
        self.display_id = race_track.canvas.create_line(coords,
                            width=self.line_width,
                            fill=self.color)
        self.blinking = True
        self.display_on()   # display, then call display_off
        
        if isinstance(entry, RoadStraight):
            self.highlight_straight()
        elif isinstance(entry, RoadTurn) and entry.is_left():
            self.highlight_left_turn()
        elif isinstance(entry, RoadTurn) and not entry.is_left():
            self.highlight_right_turn()
        else:
            raise SelectError(f"Don't know how to highlight {entry}")
        
    def highlight_straight(self):
        """ Highlight straight based on what can be done
        Selection areas, with addon road types
                         x_1                   x_2
        #########################################################                                                       X
        #(0,1)           #(.3,1)         (.7,1)#           (1,1)#
        #                #                     #                #
        #                #                     #                #
        #   LEFT TURN    #     STRAIGHT        #    RIGHT TURN  #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,.7)          #(.3,.7)       (.7,.7)#                #
        ######################################################### y_1
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #      BACKUP         #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,.3)          #(.3,.3)       (.7,.3)#          (1,.3)#
        ######################################################### y_2
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #      BACKUP         #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,0)           #(.3,0)        (.7,0) #           (1,0)#
        #########################################################
        
        """
        pos_within = self.entry.get_pos_relative(x=self.x, y=self.y)
        if not hasattr(self.entry, "edge"):
            SlTrace.lg("highlight_straight: missing attr entry.edge")
            self.entry.edge = 2
        x_min = self.entry.edge
        x_max = 1. - self.entry.edge                   
        y_min = self.entry.edge
        y_max = 1. - self.entry.edge
        x_width = x_max - x_min
        y_width = y_max - y_min
        x_1 = int(x_min + .3*x_width)
        x_2 = int(x_max - .3*x_width)
        y_1 = int(y_min + .3*y_width)
        x_2 = int(y_max - .3*y_width)
        
        position = Pt(x_min,y_min)
        xkwargs = {}
        '''left_turn_select = BlockPolygon(
            container=self.entry,
            tag=self.tag,
            position=position,
            points=[position,
                    Pt(x_min, y_max), Pt(x_max, y_max), Pt(x_max,y_min)],
            **xkwargs)
        if left_turn_select.over_us(position):
            left_turn_select.display()
        '''    

    def highlight_left_turn(self):
        """ Highlight left turn on what can be done
        Selection areas, with addon road types
        #########################################################                                                       X
        #(0,1)           #(.3,1)         (.7,1)#           (1,1)#
        #                #                     #                #
        #                #                     #                #
        #   LEFT TURN    #     STRAIGHT        #    RIGHT TURN  #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,.7)          #(.3,.7)       (.7,.7)#                #
        #########################################################
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #      BACKUP         #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,.3)          #(.3,.3)       (.7,.3)#          (1,.3)#
        #########################################################
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #      BACKUP         #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,0)           #(.3,0)        (.7,0) #           (1,0)#
        #########################################################
        
        """
        pos_within = self.entry.get_pos_relative(x=self.x, y=self.y)
        x_min = self.entry.edge
        x_max = 1. - self.entry.edge                   
        y_min = self.entry.edge
        y_max = 1. - self.entry.edge
        
        position = Pt(x_min,y_min)
        xkwargs = {}
        left_turn_select = BlockPolygon(
            container=self.entry,
            tag=self.tag,
            position=position,
            points=[position,
                    Pt(x_min, y_max), Pt(x_max, y_max), Pt(x_max,y_min)],
            **xkwargs)


    def highlight_right_turn(self):
        """ Highlight right turn on what can be done
        Selection areas, with addon road types
        #########################################################                                                       X
        #(0,1)           #(.3,1)         (.7,1)#           (1,1)#
        #                #                     #                #
        #                #                     #                #
        #   LEFT TURN    #     STRAIGHT        #    RIGHT TURN  #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,.7)          #(.3,.7)       (.7,.7)#                #
        #########################################################                                                       X
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #      BACKUP         #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #                #                     #                #
        #(0,0)           #(.3,0)        (.7,0) #           (1,0)#
        #########################################################
        
        """
        pos_within = self.entry.get_pos_relative(x=self.x, y=self.y)
        x_min = self.entry.edge
        x_max = 1. - self.entry.edge                   
        y_min = self.entry.edge
        y_max = 1. - self.entry.edge
        
        position = Pt(x_min,y_min)
        xkwargs = {}
        left_turn_select = BlockPolygon(
            container=self.entry,
            tag=self.tag,
            position=position,
            points=[position,
                    Pt(x_min, y_max), Pt(x_max, y_max), Pt(x_max,y_min)],
            **xkwargs)

                           
    def display_on(self):
        """ Show display for on_time_ms
        """
        if not self.blinking:
            return
        
        canvas = self.race_track.canvas
        canvas.itemconfigure(self.display_id, state='normal')
        self.after_id = canvas.after(self.on_time_ms,
                                           self.display_off)
        
    def display_off(self):
        """ Blank display for off_time_ms
        """
        if not self.blinking:
            return
        
        canvas = self.race_track.canvas
        canvas.itemconfigure(self.display_id, state='hidden')
        self.after_id = canvas.after(self.off_time_ms, self.display_on)
        
    def cancel(self):
        """ Turn off highlight
        """
        self.blinking = False   # Stop looping
        canvas = self.race_track.canvas
        if self.after_id is not None:
            canvas.after_cancel(self.after_id)  # Stop calls
        if self.display_id is not None:
            canvas.delete(self.display_id)
            self.display_id = None
        self.entry = None
        