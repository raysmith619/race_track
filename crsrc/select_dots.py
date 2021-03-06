"""
Created on Oct 30, 2018

@author: raysmith
Creation and Manipulation of the grid (dots and squares)
of the old dots game
"""
from select_trace import SlTrace
from select_error import SelectError
from select_area import SelectArea
from select_part import SelectPart
from canvas_tracked import CanvasTracked

class SelectDots(object):
    """
    classdocs
    """


    ###@profile    
    def __init__(self, frame, mw=None, nrows=10,
                  ncols=None,
                  width=None, height=None, tbmove=.1,
                  do_corners=True,
                  do_edges=True,
                  do_regions=True,
                  check_mod=None,
                  down_click_call=None,
                  highlight_limit=None,
                  corner_visible=True,
                  region_on_color='white',
                  region_off_color='light slate gray',
                  region_visible=False,
                  edge_width=1,
                  edge_visible=True):
        """
        :frame: - frame within we are placed
        :nrows: number of rows of squares default: 10
        :ncols: number of columns of squares default: rows
        :width: window width
        :height: window height
        :tbmove: minimum time(seconds) between move detection
        :check_mod: routine called, if present, before & after
                part modification
        :corner_visible: corner is visible default: True
        :region_on_color: color when region is "on"
        :region_off_color: color when region if "off"
        :region_visible: region (off) is visible default: False
        :highlight_limit: limit highlighting (seconds)
                default: None (None - no limit)
        :edge_width: edge width in pixels
                        default:1
        :edge_visible: edge visible default: True
        """
        self.frame = frame
        self.canvas = None
        self.mw = mw
        self.nrows = nrows
        if ncols is None:
            ncols = nrows
        self.ncols = ncols
        self.nrows = nrows
        self.ncols = ncols
        self.do_corners = do_corners
        self.do_edges = do_edges
        self.do_regions = do_regions
        if width is None:
            width = frame.winfo_width()
        self.width = width
        if height is None:
            height = frame.winfo_height()
        self.height = height
        self.drawn_lines = []           # lines drawn
            
        self. min_xlen = 10
        self.min_ylen = self.min_xlen
        self.check_mod = check_mod
        self.tbmove = tbmove
        self.highlight_limit = highlight_limit
        
        self.down_click_call = down_click_call
        self.region_on_color = region_on_color
        self.region_off_color = region_off_color
        self.region_visible = region_visible
        self.corner_visible = corner_visible
        self.edge_width = edge_width
        self.edge_visible = edge_visible
        
        self.area = None        # Set non None when created
        self.setup_area()
        
    
    def setup_area(self):
        """ Setup / resetup board setting
        """
        new_area = False            # Indicate reset
        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None 
            new_area = True
        self.canvas = CanvasTracked(self.frame,
                 width=self.width, height=self.height,
                 bg="white")
        self.canvas.pack()
        
        self.area = SelectArea(self.canvas, mw=self.mw, tbmove=self.tbmove,
                               check_mod=self.check_mod,
                               down_click_call=self.down_click_call,
                               highlight_limit=self.highlight_limit)

        rects =  []
        rects_rows = []         # So we can pass row, col
        rects_cols = []
        
        def rn(val):
            return int(round(val))
        
        xmin = .1*float(self.width)
        xmax = .9*float(self.width)
        xlen = (xmax-xmin)/float(self.ncols)
        min_xlen = float(self.min_xlen)
        if xlen < min_xlen:
            SlTrace.lg("xlen(%.0f) set to %.0f" % (xlen, min_xlen))
            xlen = min_xlen
        ymin = .1*float(self.height)
        ymax = .9*float(self.height)
        ylen = (ymax-ymin)/float(self.nrows)
        min_ylen = float(self.min_ylen)
        if ylen < min_ylen:
            SlTrace.lg("ylen(%.0f) set to %.0f" % (ylen, min_ylen))
            ylen = min_ylen
        for i in range(int(self.ncols)):
            col = i+1
            x1 = xmin + i*xlen
            x2 = x1 + xlen
            for j in range(int(self.nrows)):
                row = j+1
                y1 = ymin + j*ylen
                y2 = y1 + ylen
                rect = ((rn(x1), rn(y1)), (rn(x2), rn(y2)))
                rects.append(rect)
                rects_rows.append(row)
                rects_cols.append(col)
       
        
        for i, rect in enumerate(rects):
            row = rects_rows[i]
            col = rects_cols[i]
            self.area.add_rect(rect, row=row, col=col,
                            color=self.region_off_color,
                            do_corners=self.do_corners,
                            do_edges=self.do_edges,
                            draggable_edge=False,
                            draggable_corner=False,
                            draggable_region=False,
                            on_color=self.region_on_color,
                            off_color=self.region_off_color,   
                            invisible_region=not self.region_visible,
                            invisible_edge=not self.edge_visible,
                            edge_width=self.edge_width)
        for part in self.area.get_parts():
            if self.do_corners and part.is_corner():
                part.set(display_shape="circle",
                           display_size=self.edge_width,
                           color="blue")
                if new_area:
                    part.display()
            elif self.do_edges and part.is_edge():
                part.set(edge_width_select=50,
                           edge_width_display=self.edge_width,
                           on_highlighting=True,
                           off_highlighting=True,
                           color="lightgreen")
            elif self.do_regions and part.is_region():
                part.set(color=self.region_off_color)
                top_edge = part.get_top_edge()
                if top_edge is not None:
                    top_edge.row = part.row 
                    top_edge.col = part.col
                right_edge = part.get_right_edge()
                if right_edge is not None:
                    right_edge.row = part.row 
                    right_edge.col = part.col + 1
                botom_edge = part.get_botom_edge()
                if botom_edge is not None:
                    botom_edge.row = part.row + 1 
                    botom_edge.col = part.col
                left_edge = part.get_left_edge()
                if left_edge is not None:
                    left_edge.row = part.row 
                    left_edge.col = part.col
        self.complete_square_call = None                # Setup for complete square call
        self.new_edge_call = None                       # Setup for new edge call


    def get_part(self, id=None, type=None, sub_type=None, row=None, col=None):
        """ Get basic part
        :id: unique part id
        :type: part type e.g., edge, region, corner
        :row:  part row
        :col: part column
        :returns: part, None if not found
        """
        return self.area.get_part(id=id, type=type, sub_type=sub_type, row=row, col=col)

 
    def get_parts(self, pt_type=None):
        """ Get parts in figure
        :pt_type: part type, default: all parts
                "corner", "edge", "region"
        """
        return self.area.get_parts(pt_type=pt_type)
    
    
    def get_legal_moves(self):
        """  Get edges that would be legal moves
        """
        edges = self.get_parts(pt_type="edge")
        moves = []
        for edge in edges:
            if not edge.is_turned_on():
                moves.append(edge)
        return moves
    
    
    def get_selects(self):
        """ GEt list of selected part ids
        :returns: list, empty if none
        """
        return self.area.get_selects()


    def get_selected_part(self):
        """ Get selected part
        :returns: selected part, None if none selected
        """
        return self.area.get_selected_part()
                
    
    def get_parts_at(self, x, y, sz_type=SelectPart.SZ_SELECT):
        """ Check if any part is at canvas location provided
        If found list of parts
        :Returns: SelectPart[]
        """
        return self.area.get_parts_at(x,y,sz_type=sz_type)



    def get_xy(self):
        """ get current mouse position (or last one recongnized
        :returns: x,y on area canvas, None if never been anywhere
        """
        return self.area.get_xy()

    
    def add_complete_square_call(self, call_back):
        """ Add function to be called upon completed square
        :call_back: call back (edge, region) - None - remove call back
        """
        self.complete_square_call = call_back


    def add_down_click_call(self, call):
        """ Add down click processing function
        :call: down click processing function
        """
        self.area.add_down_click_call(call)
        
    
    def add_new_edge_call(self, call_back):
        """ Add function to be called upon newly added edge
        :call_back: call back (edge) - None - remove call back
        """
        self.new_edge_call = call_back
        
    def complete_square(self, edge, regions):
        """ Report completed square
        :edge: - edge that completed the region
        :regions: - completed region(s)
        """
        SlTrace.lg("Completed region edge=%s" % (edge), "complete_square")
        if self.complete_square_call is not None:
            self.complete_square_call(edge, regions)


    def set_down_click_call(self, down_click_call):
        """ Direct down_click processing
        """
        self.down_click_call = down_click_call


    def is_square_complete(self, edge, squares=None, ifadd=False):
        """ Determine if this edge completes a square(s)
        :edge: - potential completing edge
        :squares: list, to which any completed squares(regions) are added
                Default: no regions are added
        :returns: True iff one or more squares are completed
        """
        return self.area.is_square_complete(edge, squares=squares, ifadd=ifadd)




    def square_complete_distance(self, edge,
                                  squares_distances=None):
        """ Determine minimum number of moves, including this
        move to complete a square
        :edge: - potential completing edge
        :squares_distances: list, of (distance, square) pairs
                Default: no entries returned
                if no connected squares - empty list returned
        :returns: closest distance, NOT_CLOSE if no squares
        """
        return self.area.square_complete_distance(edge, squares_distances=squares_distances)
        
        
    def new_edge(self, edge):
        """ Report new edge added
        :edge: - edge that was added
        """
        SlTrace.lg("SelectDots.new_edge: edge=%s" % (edge), "new_edge")
        if self.new_edge_call is not None:
            self.new_edge_call(edge)
        self.area.stroke_info.setup()      # Reset stroke search


    def disable_moves(self):
        """ Disable(ignore) moves by user
        """
        self.area.disable_moves()
        
        
    def enable_moves(self):
        """ Enable moves by user
        """
        self.area.enable_moves()


        
    def down_click(self, part, event=None):
        """ Process down click over highlighted part
        All highlighted parts elicit a call
        :part: highlighted part
        :event: event if available
        :Returns: True if processing is complete
        """
        if self.down_click_call is not None:
            return self.down_click_call(part, event=event)
        
        """ Self processing
        """
        if part.is_edge() and not part.is_turned_on():
            SlTrace.lg("turning on %s" % part, "turning_on")
            self.drawn_lines.append(part)
            part.turn_on()
            regions = part.get_adjacents()      # Look if we completed any squares
            for square in regions:
                if square.is_complete():
                    self.complete_square(part, square)
                    
            return True             # Indicate processing is done
    
        return False
        

    def stroke_call(self, part=None, x=None, y=None):
        """ Call back from sel_area.add_stroke_call
        """
        
        self.down_click(part)
        
            
    def display(self):
            self.area.display()


    def destroy(self):
        if self.area is not None:
            self.area.destroy()
            self.area = None
        if self.canvas is not None:
            self.canvas.destroy()
            self.canvas = None
    

    def remove_parts(self, parts):
        """ Remove deleted or changed parts
        Only clears display, leaving part in place
        :parts: list of parts to be removed
        """
        return          # aLL changes reflected by insert
        for part in parts:
            d_part = self.area.get_part(id=part.part_id)
            if d_part is None:
                raise SelectError("No part(id=%d) found %s"
                                   % (part.part_id, part))
                continue
            d_part.turn_off()
            d_part.highlight_clear(display=False)
            d_part.display_clear()
            d_part.set(invisible=True)


    def reset(self):
        """ Set board to beginning of game
        """
        self.setup_area()
        '''
        regions = self.area.get_parts(pt_type="region")
        for region in regions:
            region.display_clear()
        edges = self.area.get_parts(pt_type="edge")
        for edge in edges:
            edge.turn_off()
            edge.select_clear()
            edge.highlight_clear()
            edge.display_clear()
        '''
            
    def insert_parts(self, parts):
        """ Add new or changed parts
        Replaces part of same id, redisplaying
        :parts: list of parts to be env_added
        """
        for part in parts:
            d_part = self.area.get_part(id=part.part_id)
            if d_part is None:
                raise SelectError("insert_parts: No part(id=%d) found %s"
                                   % (part.part_id, part))
                continue
            self.set_part(part)
        
        
    def select_clear(self, parts=None):
        """ Select part(s)
        :parts: part or list of parts
                default: all selected
        """
        self.area.select_clear(parts=parts)


    def select_set(self, parts, keep=False):
        """ Select part(s)
        :parts: part(s) to select/deselect
        """
        self.area.select_set(parts, keep=keep)
        
        
        

    def set_part(self, part):
        """ Set base part.contents to values of Part
        
        :part: part structure with new values
        """
        pt = self.area.parts_by_id[part.part_id]
        if pt is None:
            SlTrace.lg("part %s(%d) is not in area - skipped"
                       % (part, part.part_id))
            return

        pt.__dict__ = part.__dict__.copy()
        
        
    
    
    def set_stroke_move(self, use_stroke=True):
        """ Enable/Disable use of stroke moves
        Generally for use in touch screens
        """
        self.area.set_stroke_move(use_stroke)
        