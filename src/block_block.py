# block_block.py        

from enum import Enum
import copy
from homcoord import *
import sys, traceback


from select_trace import SlTrace
from select_error import SelectError


class BlockType(Enum):
    COMPOSITE = 1
    POLYGON = 2
    LINE = 3
    ARC = 4
    CHECK = 5

def tran2matrix(tran):
    """ Display tran's matrix
    :tran: transform
    """
    if tran is None:
        return "None"
    
    return "%s" % tran._m


class SelectInfo:
    """ Selected block information
    Used to provide operation on selected objects
    """
    
    def __init__(self, block=None, x_coord=None, y_coord=None, x_coord_prev=None,  y_coord_prev=None,
                 prev_select=None):
        """ Selction info
        :block: selected block
        :x_coord: x-coordinate on canvas
        :y_coord: y-coordinate
        :x_coord_prev: previous mouse x_coord
        :y_coord_prev: previous y_coord
        :prev_select: previously selected SelectInfo
        """
        self.block = block
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

        
    def __repr__(self):
        str_str = "%s" % self.block
        return str_str
        
    def __str__(self):
        str_str = "%s" % self.block
        return str_str


   
class BlockBlock:
    """
    A BlockBlock is a composite of geometrical things (currently 2-dimensional) 
    which can be used to construct hierarchical graphical objects
    Object properties are expressed in relation to the containing object (container),
    if one, else in relation to the canvas (cv_width, cv_height)  The values of
    cv_width, cv_height are needed because canvas.wininfo are not always available.
    
    Internal coordinate system is Cartesian:
         x to left, y to up
         x=0: right side, y=0: botom
    
      position    Pt()  within container
      width       0.to 1 of container width
      height      0. to 1 of container height
      color        default color
      rotation    rotation (degrees counter clockwise) relative to container
                  0 = pointing to right (positive x)
      velocity    velocity: x,y / second
    internal:
      base_xtran - homogenous transform when needed
    When a BlockBlock moves/rotates The components move/rotate accordingly
    """
    id = 0
    canvas = None           # Builtin canvas reference
    tagged_blocks = {}      # Displayed blocks, by canvas tag
    id_blocks = {}          # Blocks by block id
    selects = {}            # ids of selected blocks
    selects_list = []       # SelectInfo blocks in order of selection
                            # Adjusted by set_selected, clear_selected
    aux_canvas_tags = {}    # Extra tags for debugging, etc


    @classmethod
    def set_canvas(cls, canvas):
        """ Setup for base methods
        :canvas: canvas object
        """
        cls.canvas = canvas
        
    @classmethod
    def cls_get_canvas(cls):
        if cls.canvas is None:
            raise SelectError("No canvas set")
        
        return cls.canvas


    @classmethod
    def mkpoint(cls, x,y, color="red", rad=5):
        """ Make a marker
        :color: marker color default: red
        :rad:  radius of point default: radius (pixels)
        :returns: tag created
        """
        canvas = cls.cls_get_canvas()
        x0 = x-rad
        y0 = y-rad
        x1 = x+rad
        y1 = y+rad
        tag = canvas.create_oval(x0,y0,x1,y1, fill=color)
        cls.aux_canvas_tags[tag] = tag
        return tag
    
    @classmethod
    def new_id(cls):
        BlockBlock.id += 1
        return BlockBlock.id
    
    
    @classmethod
    def get_xtran(self, comp):
        """ Get transformation of comp + containers
        :comp: componenet whos transform is desired
        :returns: transform from top to comp
        """
        comps = [comp]
        while comp.container is not None:
            comps.insert(0, comp.container)
            comp = comp.container
        
        xtran = None
        for comp in comps:
            xtran_next = comp.base_xtran()
            if xtran_next is not None:
                if xtran is None:
                    xtran =xtran_next
                else:
                    xtran = xtran.compose(xtran_next)
        return xtran


    @classmethod
    def xtran(cls, translate=None, rotate=None, scale=None):
        """ Create translation matrix for local entity which is
        translated via Pt(x,y), rotated rotate degrees, then scaled via Pt(x,y)
        :translate: translation Pt(x,y) default: no translation
        :rotate: rotation(degrees) counter clockwise default: no rotation
        :scale:  scale (Pt(x,y) default: no scaling
        :returns: translation matrix default: Ident
        """
        xtran = Xlate(0,0)
        if scale is not None:
            xst = Xscale(scale.xy)
            xtran = xtran.compose(xst)
        if rotate is not None:
            xrt = Xrotate(radians(rotate))
            xtran = xtran.compose(xrt)
        if translate is not None:
            xft = Xlate(translate.xy)
            xtran = xtran.compose(xft)
        return xtran

    
    @classmethod
    def get_transform(cls, block):
        comp = block
        comps = [comp]      # bottom ... top
        while comp.container is not None:
            comps.append(comp.container)
            comp = comp.container
        xtrans = []
        for comp in comps:
            xtrans.append(comp.base_xtran())
        xtrans.reverse()        # Place top ... bottom
        xtran = None
        for xt in xtrans:   
            if xtran is None:
                xtran = xt
            else:
                xtran = xtran.compose(xt)
        return xtran

    ''' Trying Inv(A)*Inv()...
    @classmethod
    def get_transform_inverse(cls, block):
        xtran = BlockBlock.get_transform(block)
        if xtran is None:
            return xtran        # No translation
        
        SlTrace.lg("xtran = %s" % tran2matrix(xtran))
        
        comp = block
        comps = [comp]      # bottom ... top
        while comp.container is not None:
            comps.append(comp.container)
            comp = comp.container
        ixtrans = []
        for comp in comps:
            xtran =comp.base_xtran()
            ixtran = xtran.inverse()
            ixtrans.append(ixtran)
        ###ixtrans.reverse()        # Place top ... bottom
        ixtran = None
        for ixt in ixtrans:   
            if ixtran is None:
                ixtran = ixt
            else:
                ixtran = ixtran.compose(ixt)
 
        SlTrace.lg("ixtran = %s" % tran2matrix(ixtran))
        xtran_ti = xtran * ixtran
        SlTrace.lg("xtran * ixtran=%s" % tran2matrix(xtran_ti))
        return ixtran
    '''
    
    @classmethod
    def get_transform_inverse(cls, block):
        xtran = BlockBlock.get_transform(block)
        if xtran is None:
            return xtran        # No translation
        
        SlTrace.lg("xtran = %s" % tran2matrix(xtran))
        ixtran = xtran.inverse()
        SlTrace.lg("ixtran = %s" % tran2matrix(ixtran))
        xtran_ti = xtran * ixtran
        SlTrace.lg("xtran * ixtran=%s" % tran2matrix(xtran_ti))
        return ixtran
    
   
   
    @classmethod
    def transform_points(cls, xtrans, points=None):
        """ Transform point/points via one or more transformations
        :xtran: trans form or list of transforms
        :points: point or list of points to transform
        :returns: transformed point if points is one else list of transformed points
        """
        xtran = None
        if not isinstance(xtrans, list):
            xtran = xtrans           # Just one
        else:
            for xt in xtrans:
                if xtran is None:
                    xtran = xt
                else:
                    xtran = xtran.compose(xt)
        if not isinstance(points, list):
            pt = xtran.apply(points)
            return pt
        
        pts = []
        for point in points:
            pt = xtran.apply(point)
            pts.append(pt)
        return pts


        
        
    @classmethod
    def set_selected(cls, block_block_id, x_coord=None, y_coord=None, x_coord_prev=None,
                     y_coord_prev=None, keep_old=False, display=True):
        """ Set/add block to selected blocks
        :block_block_id: block/block_id to be added
        :x_coord: x canvas coordinate
        :y_coord: y canvas coordinate
        :x_coord_prev: previous x coordinate default: x_coord
        :y_coord_prev: previous y coordinate default: y_coord
        :keep_old: keep old selected default: False (drop previously selected)
                    In any event, only drop selections from same origin
        :display: display object afer change, default: True
        :returns: reference to new selection entry
        """
        if block_block_id is None:
            raise SelectError("set_selected with block_id is None")
        if isinstance(block_block_id, int):
            block_id = block_block_id
            block = cls.id_blocks[block_id]
        else:
            block = block_block_id
            block_id = block.id
        if not block_id in cls.id_blocks:
            raise SelectError("get_selected id(%d) has no block" % block_id)
        
        if not keep_old:
            select_origin = block.origin
            sids = list(cls.selects.keys())
            for sid in sids:
                if sid in cls.selects:
                    sid_block = cls.selects[sid].block
                    if sid_block.origin == select_origin:
                        SlTrace.lg("Clearing selected %s" % sid_block)
                        cls.clear_selected(sid)
        if x_coord is None:
            if block is not None:
                x_coord, y_coord = block.position.xy    # Use block position               
        selected = SelectInfo(block=block, x_coord=x_coord, y_coord=y_coord,
                              x_coord_prev=x_coord_prev, y_coord_prev=y_coord_prev)
        cls.selects[block.id] = selected
        cls.selects_list.append(selected)
        ### Redundant ??? block.selected = True
        if SlTrace.trace("selected"):
            SlTrace.lg("set_selected(%s)"  % block)
        if SlTrace.trace("set_selected_stack"):
            stack_str = ''.join(traceback.format_stack())
            SlTrace.lg("\nset_selected_stack: %s" % stack_str)                    
        if display:
            block.display()
        return selected
    

    @classmethod
    def clear_selected(cls, bid=None, origin=None, display=True):
        """ Clear (unset) selected block
            May do some visual stuff in the future
        :bid:  block id, default: clear all selected blocks
        :origin: clear only if origin match default: all
        """
        if bid is None:
            sids = list(cls.selects.keys())
            for sid in sids:
                if origin is None or origin == cls.id_blocks[sid].origin:
                    cls.clear_selected_block(sid, display=display)
        else:
            cls.clear_selected_block(bid, display=display)        


    @classmethod
    def clear_selected_block(cls, bid, display=True):
        """ clear specified block
        :bid: block id to clear selected
        """
        if not bid in cls.id_blocks:
            return
                
        block = cls.id_blocks[bid]
        comp = block
        while comp is not None:
            blk_id = comp.id
            if blk_id in cls.id_blocks and blk_id in cls.selects:
                # Remove corresponding entry in list
                del cls.selects[blk_id]
                for i, selent in enumerate(cls.selects_list):
                    if blk_id == selent.block.id:
                        del cls.selects_list[i]
                        if display:
                            comp.display()
                        return
                
            comp = comp.container


    @classmethod
    def get_selected_blocks(cls, origin=None):
        """ Return list of blocks currently selected
        """
        blocks = []
        for select in cls.selects_list:
            if origin is None or select.block.origin == origin:
                blocks.append(select.block)
        return blocks
        

    @classmethod
    def get_selected(cls, block=None, origin=None):
        """ Get selected info, block if selected, else None
        :block:  block to check.
        :origin: limit selection to blocks with matching origin default: any origin
        """
        if block is None:
            if origin is None:
                return list(cls.selects.values())
            
            selecteds = []
            for selected in cls.selects.values():
                if selected.block.origin == origin:
                    selecteds.append(selected)
            return selecteds
    
        selected = None
        for sid in cls.selects:
            selected = cls.selects[sid]
            if selected.block.id == sid:
                break
        if selected is None:
            return None    
        
        if selected.block is None:
            raise SelectError("selected with None for block")
       
        if selected.x_coord is None:
            SlTrace.lg("selected with None for x_coord")
            cv_width = cls.get_cv_width()
            cv_height = cls.get_cv_height()
            selected = SelectInfo(block=None, x_coord=cv_width/2, y_coord=cv_height/2)  # HACK
        return selected

           
           
    @classmethod
    def is_selected_block(cls, block):
        """ Determine if block is selected
        Is selected if it or any in container tree is in cls.selects
        """
        comp = block
        while comp is not None:
            if comp.id in cls.selects:
                return True
            comp = comp.container
        return False
                
        
            
    def __init__(self,
                 canvas=None,
                 cv_width=None,
                 cv_height=None,
                 color=None,
                 container=None,
                 ctype=BlockType.COMPOSITE,
                 position=None,
                 width=None, height=None,
                 rotation=None,
                 velocity=None,
                 visible=True,
                 tag=None,
                 background=None,
                 origin=None,
                 selected=False,
                 state=None,
                 xkwargs=None):
        """ Setup object
        :canvas: optional canvas argument - provides Canvas if no container
        :cv_width: optional canvas width
        :cv_height: optional canvas height
        :color:  block's basic color
        :container: containing object(BlockBlock), default: this is the base object
        :ctype: container type defalut:COMPOSITE
        :width: width as a fraction of container's width dimensions'
                e.g. 1,1 with container==None ==> block is whole canvas
                If container is None
                    width = width * self.cv_width
        :height" height as a fraction of container's height
        :position: position of lower left corner(x=0, y=0) relative to container's position (x=0, y=0)
        :rotation:  rotation relative to container's rotation
        :velocity:  velocity relative to container's velocity
        :visible:   visible iff container's visible default: seen
        :points:    points, used for this component
        :tag:    Optional identifier  default: class name
        :background:  background color, if asked
        :origin:  Origin/local of block/object e.g. road_bin, road_track, car_bin
        :selected: True iff object is selected default: False
        :state:   State of object e.g. "new", "moved"
        :xkwargs:   optional canvas operation args (dictionary to avoid name
                                                    collisions)
        """
        self.canvas_tags = {}           # tags if any displayed
        self.origin = origin            # Set by others
        self.selected = False
        self.state = state              # Set by others
        self.id = BlockBlock.new_id()
        if tag is None:
            tag = self.__class__.__name__
        self.tag = tag
        self.canvas = canvas
        self.cv_width = cv_width
        self.cv_height = cv_height
        self.color = color
        self.container = container
        if container is None:
            SlTrace.lg("block: %s has None container" % self)
        if background is None:
            background = "white"
        self.background = background
        if SlTrace.trace("block_create"):
            SlTrace.lg("\nBlockBlock[%d]:%s %s %s container: %s" % (self.id, tag, ctype, self, container))
            SlTrace.lg("tag_list: %s" % self.get_tag_list())    
        self.comps = []     # List of components
        self.ctype = ctype

        if width is not None or height is not None: # Any scaling ?
            if width is None:
                width = height          # same
            if height is None:
                height = width          # same
        
        if container is None:               # Top of heap ?
            if width is not None:               # Any scaling
                width *= self.get_cv_width()          # Scale width to canvas
                height *= self.get_cv_length()            
                        
        self.position = position
        self.width = width
        self.height = height
        self.velocity = velocity
        self.rotation = rotation        
        self.visible = visible
        if xkwargs is None:
            xkwargs = {}
        self.xkwargs = xkwargs
        ###self.xtran = self.base_xtran()     # Setup this component's translation matrix
        ###self.xtran = BlockBlock.get_xtran(self)


    def __str__(self):
        str_str = self.__class__.__name__ + " id:%s" % self.id
        if hasattr(self, "origin") and self.origin is not None:
            str_str += " in:%s" % self.origin
        if hasattr(self, "state") and self.state is not None:
            str_str += " state:%s" % self.state
        return str_str
    
    
    def get_tag_list(self):
        """ List of tags from top container to this component
        """
        tag_list = self.tag
        comp = self
        while comp.container is not None:
            comp = comp.container
            tag_list = comp.tag + ":" + tag_list
        return tag_list


    def get_top_container(self):
        """ Get top containing block
        :returns: top container, self if no container
        """
        top = comp = self
        while comp.container is not None:
            top = comp = comp.container
        return top

        
    def get_infront_coords(self):
        """ Adhock "infront point"
        
        :return coordinates (within candidate block)
        simulate Pt(.5, 1+fraction) which doesn't seem to work
        """
        fraction = .2                   # Ammount in front as a fraction of our height
        ppcs = self.get_perimeter_coords()
        x0,y0 = ppcs[0], ppcs[1]        # 0,0 lower left corner (box coordinates(0,0))
        x1, y1 = ppcs[2], ppcs[3]       # 1,0 Upper left corner (box coordinates)
        x2, y2 = ppcs[4], ppcs[5]       # 1,1 Upper right corner
        x3, y3 = ppcs[6], ppcs[7]       # 1,0 Lower right corner
        middle_top_coords = [(x1+x2)/2., (y1+y2)/2.]
        middle_bottom_coords = [(x0+x3)/2., (y0+y3)/2.]
        SlTrace.lg("middle_top: %s middle_bottom: %s" % (middle_top_coords, middle_bottom_coords))
        bottom_to_top = [middle_top_coords[0]-middle_bottom_coords[0],
                          middle_top_coords[1]-middle_bottom_coords[1]]
        bottom_to_top_fract = [bottom_to_top[0]*fraction, bottom_to_top[1]*fraction]
        infront_coords = [middle_top_coords[0]+bottom_to_top_fract[0],
                               middle_top_coords[1]+bottom_to_top_fract[1]]
        return infront_coords


    def get_position_coords(self):
        """ Provide absolute canvas coordinates of block's position
        :returns: return coordinate list(x,y) of coordinates
        """
        abs_pos = self.get_absolute_position()
        abs_pos_coords = self.pts2coords(abs_pos)
        return abs_pos_coords
        
    
    
    def get_absolute_position(self):
        """ Get block position in absolute form
        :returns: Pt(x,y) in canvas dimensions
        """
        xs = 1.
        ys = 1.
        if self.position is None:
            position = Pt(0,0)
        else:
            position = self.position
        comp = self
        while comp.container is not None:
            comp = comp.container
            if comp.width is not None:
                xs *= comp.width
            if comp.height is not None:
                ys *= comp.height
        return Pt(position.x*xs, position.y*ys)  
        
        

    def get_absolute_points(self, points=None):
        """ Get points in top level (canvas) reference
        :points: base point/points to translate
                default: self.points
        :returns: list of canvas points
        """
        if points is None:
            if not hasattr(self, "points"):
                points = self.get_perimeter_points()  # Boundaries
            else:
                points = self.points

        if not isinstance(points, list):
            points = [points] 
        comp = self
        comps = [comp]      # bottom ... top
        while comp.container is not None:
            comps.append(comp.container)
            comp = comp.container
        if SlTrace.trace("short_points") and len(points) < 10:
            SlTrace.lg("\nget_absolute_points(%s) comps:%s" % (points, self.get_tag_list()), "get_absolute_points")
        elif SlTrace.trace("display_points"):            
            SlTrace.lg("\ndisplay polygon points[%s]=%s" % (self.get_tag_list(), self.points), "get_absolute_points")
        xtrans = []
        for comp in comps:
            xtrans.append(comp.base_xtran())
        xtrans.reverse()        # Place top ... bottom
        abspts = BlockBlock.transform_points(xtrans, points)
        return abspts
    
    
        xtran = None
        for cp in comps:
            b_xtran = cp.base_xtran()
            if b_xtran is None:
                SlTrace.lg("cp: %s     base_xtran: %s" % (cp.get_tag_list(), b_xtran), "get_absolute_points")
            else:
                SlTrace.lg("cp: %s     base_xtran: %s" % (cp.get_tag_list(), b_xtran), "get_absolute_points")
                cpx = cp
                while cpx is not None:
                    SlTrace.lg("                   %s: width=%.2f height=%.2f position=%s"
                                % (cpx.tag, cpx.width, cpx.height, cpx.position), "get_absolute_points")
                    cpx = cpx.container
                SlTrace.lg("                _m: %s" % tran2matrix(b_xtran), "get_absolute_points")
            if b_xtran is not None:
                if xtran is not None:
                    xtran = xtran.compose(b_xtran)
                else:
                    xtran = b_xtran
            SlTrace.lg("effective xtran=%s" % xtran)
            SlTrace.lg("effective _m:%s" % tran2matrix(xtran))
        SlTrace.lg("composite _m:%s" % tran2matrix(xtran))
        pts = []     # x1,y1, x2,y2, list
        for point in points:
            pt = xtran.apply(point)
            pts.append(pt)
        if SlTrace.trace("get_absolute_points"):
            if SlTrace.trace("short_points"):
                SlTrace.lg("\nabsolute_points(%s) comps:%s" % (pts[:10], self.get_tag_list()))
            elif SlTrace.trace("display_points"):            
                SlTrace.lg("\nabsolute points[%s]=%s" % (self.get_tag_list(), pts))
        return pts


    def get_coords(self, internal_points=None):
        """ Return coordinates, given internal points, e.g., 0,0 == local version of position()
        :internal_points: points relative to block 0,0 -> lower left corner, 1,1 upper right corner
                default: perimeter
        """
        if internal_points is None:
            internal_points = self.get_perimeter_points()
        abs_points = self.get_absolute_points(internal_points)
        coords = self.pts2coords(abs_points)
        return coords
    

    def get_center_coords(self):
        points = self.get_absolute_points()
        p_x, p_y = points[0].xy
        for point in points[1:]:
            p_x += point.x
            p_y += point.y
        p_x /= len(points)
        p_y /= len(points)
        pt = Pt(p_x, p_y)
        coords = self.pts2coords(pt)
        return coords

    ''' Replaced, temporaily, with the HACK below
    until I can figure how to do it right (get_inverse_points does not work)

    def get_internal_points(self, coords):
        """ Get internal points (x=>1, y=>1) given external coordinates
        :coords:  canvas coordinates
        :returns: internal points
        """
        pts = self.coords2pts(coords)
        points = self.get_inverse_points(points=pts)
        return points
    '''

    def get_internal_points(self, coords):
        """ A HACK to get around problem with get_inverse_points
        """
        """ Get internal points (x=>1, y=>1) given external coordinates
        :coords:  canvas coordinates
        :returns: internal points
        """
        internal_pts = self.get_perimeter_points()
        abs_pts = self.get_absolute_points(internal_pts)
        up_vect = abs_pts[1] - abs_pts[0]
        up_dist = sqrt(up_vect.x**2 + up_vect.y**2)
        right_vect = abs_pts[3] - abs_pts[0]
        right_dist = sqrt(right_vect.x**2 + right_vect.y**2)
        int_points = []
        for ic in range(0, len(coords), 2):
            pt = self.coords2pts(coords[ic:ic+2])[0]
            pt_vect = pt - abs_pts[0]
            x = dot([pt_vect.x, pt_vect.y], [right_vect.x,right_vect.y])/right_dist**2
            y = dot([pt_vect.x,pt_vect.y], [up_vect.x,up_vect.y])/up_dist**2
            int_pt = Pt(x,y)
            int_points.append(int_pt)
        return int_points


    def get_internal_point(self, coords=None):
        """ get internal point from coord
        :coords: x,y pair
        :returns: internal point
        """
        pts = self.get_internal_points(coords=coords)
        return pts[0]
        
    
    def get_inverse_points(self, points=None):
        """ Get points relative to container's coordinate system
            based on absolute points
        :points: absolute(canvas) point/points to translate
                REQUIRED
        :returns: list of relative points
        """
        if points is None:
            raise SelectError("points, required, is missing")

        if not isinstance(points, list):
            points = [points]
        xtran_inverse = self.get_full_ixtran() 
        relpts = BlockBlock.transform_points(xtran_inverse, points)
        return relpts
        

    def get_inverse_point(self, pt):
        """ get single point, given an absolute point, relative to current position        :pt: current relative point
        :returns: point in container's reference
        """
        pts = self.get_inverse_points(pt)
        return pts[0]
        

    def get_absolute_point(self, pt):
        """ get single point relative to current position
        :pt: current relative point
        :returns: point in container's reference
        """
        pts = self.get_absolute_points(pt)
        return pts[0]


    def get_full_xtran(self):
        """ Get full transform from top level through this component
        """
        return BlockBlock.get_transform(self)


    def get_full_ixtran(self):
        """ Get full inverse transform from top level through this component
        """
        return BlockBlock.get_transform_inverse(self)

    def get_length(self):
        """ Get length, relative to its container, of this block
        :returns: relative rotation in degrees
        """
        length = 1. if self.height is None else self.height
        return length

    def get_width(self):
        """ Get length, relative to its container, of this block
        :returns: relative rotation in degrees
        """
        width = 1. if self.width is None else self.width
        return width


    def get_length_dist(self):
        """ Determine traversal length as fraction of container's length for the road
        """
        return self.get_length()
    

    def get_relative_points(self, points=None):
        """ Get points based on current block position
        :points: base point/points to translate
                defajlt: self.points
        :returns: list of translated points
                e.g. if default gives points as transformed
                by base transform
        """
        if points is None:
            points = self.get_points()
        if not isinstance(points, list):
            points = [points] 
        xtran = self.base_xtran()
        if xtran is None:
            return points
        
        pts = []
        position = Pt(0,0) if self.position is None else self.position
        rotation = 0. if self.rotation is None else self.rotation
        width = 1. if self.width is None else self.width
        height = 1. if self.height is None else self.height
        rtran = Xrotate(radians(rotation))
        stran = Xscale(width, height)
        ttran = Xlate(position.x, position.y)
        xtran = rtran * stran * ttran
        
        for pt in points:
            pt_x = xtran.apply(pt)
            pts.append(pt_x)
        return pts

    
    def get_relative_point(self, *ptxy):
        """ get single point relative to current position
        :ptxy: current relative point or xy pair
        :returns: point in container's reference
        """
        if len(ptxy)== 1 and isinstance(ptxy[0], Pt):
            pt = ptxy[0]
        else:
            pt = Pt(ptxy[0], ptxy[1])
        pts = self.get_relative_points(pt)
        return pts[0]

    def get_rotation(self):
        """ Get rotation, relative to its container, of this block
        :returns: relative rotation in degrees
        """
        rotation = 0. if self.rotation is None else self.rotation
        rotation %= 360.
        return rotation

    def set_rotation(self, rotation=None):
        """ Get rotation, relative to its container, of this block
        :rotation: rotation, in degrees, to set
        :returns: rotation
        """
        self.rotation = rotation
        return rotation
        
        
    def get_front_addon_rotation(self):
        """ Get rotation for a forward "addon" block
        :returns: rotation of addon block in containers reference
                    None if no rotation, treated as 0. deg
        """
        return self.get_rotation()

    def get_perimeter_points(self):
        """ Returns a set of internal points (relative to this block)
        usable for determining inside/outside
        """
        return [Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)]

    def get_perimeter_abs_points(self):
        """ Returns a set of coordinates (relative to this block)
        usable for determining inside/outside
        """
        internal_points = self.get_perimeter_points()
        abs_points = self.get_absolute_points(internal_points)
        return abs_points

    def get_perimeter_coords(self):
        """ Returns a set of coordinates (relative to this block)
        usable for determining inside/outside
        """
        abs_points = self.get_perimeter_abs_points()
        coords = self.pts2coords(abs_points)
        return coords

    def get_back_addon_position(self, new_type=None):
        """ Get point on which to place a new back "addon" block
        so as to have the back block be a "front_addon_to the new block"
        :returns: point (Pt) in containers reference 
        """
        raise SelectError("get_back_addon_position Not yet implemented")
    
        internal_pt = Pt(0,1)
        rot = self.get_rotation()   # TFD to see what happens
        if rot != 0 and rot != 180:
            internal_pt = Pt(0,1*2)  
        add_pt = self.get_relative_point(internal_pt)
        if SlTrace.trace("get_front_addon"):
            ###container = self.container if self.container is not None else self
            SlTrace.lg("get_front_addon_position %s = %s(%s)" %
                        (self, add_pt, self.get_absolute_point(internal_pt)))
        return add_pt


    def get_front_addon_position(self, nlengths=1):
        """ Get point on which to place a forward "addon" block
        :nlengths: number of lengths forward default:1
        :returns: point (Pt) in containers reference 
        """
        internal_pt = Pt(0,1*nlengths)
        rot = self.get_rotation()   # TFD to see what happens
        if rot != 0 and rot != 180:
            internal_pt = Pt(0,1*2)  
        add_pt = self.get_relative_point(internal_pt)
        if SlTrace.trace("get_front_addon"):
            ###container = self.container if self.container is not None else self
            SlTrace.lg("get_front_addon_position %s = %s(%s)" %
                        (self, add_pt, self.get_absolute_point(internal_pt)))
        return add_pt
    
      
    def abs_front_pos(self):
        """ Get absolute xy canvas coordinates of front addon position
        These are canvas coordinates of relative position
        returned by get_front_addon_position()
        :returns: list of coordinates x,y
        """
        add_pos = self.get_front_addon_position()
        container = self.container if self.container is not None else self
        abs_add_pos = container.get_absolute_point(add_pos)
        pos_coords = self.pts2coords(abs_add_pos)
        return pos_coords
    
    
    def get_top_left(self):
        """ Get top left corner in container's  terms
        so container can use next_entry(position=previous_entry.get_top_left()...) to place next_entry on
        the top left of previous entry.
        """
        tlc = self.get_relative_point(Pt(0,1))
        if SlTrace.trace("add_block"):
            container = self.container if self.container is not None else self
            SlTrace.lg("get_top_left %s = %s(%s)" %
                        (self.get_tag_list(), tlc, container.get_absolute_point(tlc)))
        return tlc


    def get_top_right(self):
        """ Get top left corner 
        """
        trc = self.get_relative_point(Pt(1,1))
        return trc
    
    
    def get_canvas(self):
        """ Get our canvas
        :returns: canvas, None if no canvas or top
        """
        top = self.get_top_container()
        SlTrace.lg("get_canvas: top:%s selects:%s" % (top, self.selects), "get_canvas")
        return top.canvas
    
    
    def get_cv_height(self):
        """ Return canvas height (or projected height)
        """
        top = self.get_top_container()
        cv_height = top.cv_height
        if cv_height is None:
            cv_height = 600
        return cv_height
 
 
    def get_cv_length(self):
        """ same as get_cv_height
        """
        return self.get_cv_height()
    
    
    def get_cv_width(self):
        """ Return canvas width (or projected width)
        """
        top = self.get_top_container()
        if not hasattr(top, "cv_width"):
            raise SelectError("has no cv_width")
        cv_width = top.cv_width
        if cv_width is None:
            cv_width = 1.
        return cv_width


    def has_canvas(self):
        """ Determine if this object has a canvas
        """        
        top = self.get_top_container()
        if hasattr(top, "canvas"):
            return True
        
        return False


    def is_at(self, x=None, y=None, level=0, max_level=10, margin=None):
        """ Check if point(x,y) is within the block or
            its components
        :x: canvas x coordinate
        :y: canvas y coordinate
        :level: recursion depth
        :max_level: maximum depth, in case we have recursive construction
        :margin: margin +/- in x,y default: none ==> 0
        """
        level += 1
        if level > max_level:
            return False
        
        if x is None:
            raise SelectError("is_at is missing a required parameter x")
        
        if y is None:
            raise SelectError("is_at is missing a required parameter y")
            
        if self.ctype == BlockType.COMPOSITE:
            for comp in self.comps:
                if comp.is_at(x=x, y=y, level=level+1, margin=margin):
                    return True         # component is at x,y
            
            return False                # No component is at x,y
        
        # Treat as base component 
        # rough guess treet as square
        # For now assume alligned with x and y axes
        min_x, min_y, max_x, max_y = self.min_max_xy()
        if margin is not None:
            min_x -= margin
            min_y -= margin
            max_x += margin
            max_y += margin
        if (x >= min_x and x <= max_x
                and y >= min_y and y <= max_y):
            return True
        
        return False


    def min_max_xy(self):
        """ Returns min_x, min_y, max_x, max_y canvas coordinates
        """
        abs_points = self.get_absolute_points()
        abs_coords = self.pts2coords(abs_points)
        abs_x_coords = []
        abs_y_coords = []
        for i in range(len(abs_coords)):
            if i % 2 == 0:
                abs_x_coords.append(abs_coords[i])
            else:
                abs_y_coords.append(abs_coords[i])
        max_x = max(abs_x_coords)
        min_x = min(abs_x_coords)
        min_y = min(abs_y_coords)
        max_y = max(abs_y_coords)
        return (min_x,min_y,max_x,max_y)
        
    
    def is_selected(self):
        """ Check if selected or any in the container chain is
        selected
        """
        return self.is_selected_block(self)

               
    def base_xtran(self):
        """ Create this component's contribution
        to the translation:
        Use local coordinate frame
            v' = M x v = R x T x S x v
        Result:
            self.xtran is None if no translation
            self.xtran == translation for this component (before sub parts such as points)
        """
        SlTrace.lg("\nbase_xtran: %s" % self, "base_xtran")
        width = self.width
        if width is None:
            width = 1.
        height = self.height
        if height is None:
            height = 1.
        position = self.position
        rotation = self.rotation
        if rotation is None:
            rotation = 0
        position = self.get_absolute_position()
        SlTrace.lg("base_xtran: %s translate=%s, rotate=%.1f, scale=(%.1f, %.1f)"
                    % (self.tag, position, rotation, width, height), "base_xtran")
        return BlockBlock.xtran(translate=position,
                                rotate=rotation, scale=Pt(width,height))
        ''' Use class function
        comp = self
        comps = []                  # Scale through all containers
        while comp.container is not None:
            comps.insert(0, comp.container)
            comp = comp.container
        
        scale_x = 1.
        scale_y = 1.
        for comp in comps:
            if comp.width is not None:
                scale_x *= comp.width
            if comp.height is not None:
                scale_y *= comp.height
        
        xtran = None                # Changed if any scaling
        if rotation is not None:
            xfr = Xrotate(radians(rotation))
            SlTrace.lg("xfr=%s" % xfr)
            SlTrace.lg("    _m:%s" % tran2matrix(xfr))
            if xtran is None:
                xtran = xfr                                 # Start with this transform
            else:
                xtran = xtran.compose(xfr)        # Add this transform
            SlTrace.lg("xtran=%s" % xtran)
            SlTrace.lg("    _m:%s" % tran2matrix(xtran))
        if position is not None:
            x_n = scale_x*position.x
            y_n = scale_y*position.y
            SlTrace.lg("scale_x=%.2f scale_y=%.2f position(%.2f,%.2f)"
                        % (scale_x, scale_y, x_n, y_n))
            xft = Xlate(x_n, y_n)    # Move to origin
            SlTrace.lg("    _m:%s" % tran2matrix(xft))
            if xtran is None:
                xtran = xft
            else:
                xtran = xtran.compose(xft)
            SlTrace.lg("xtran=%s" % xtran)
            SlTrace.lg("    _m:%s" % tran2matrix(xtran))
        if width is not None:       # width and height or none
            xfs = Xscale(scale_x, scale_y)                       # Scale by comp size
            SlTrace.lg("xfs=%s" % xfs)
            SlTrace.lg("    _m:%s" % tran2matrix(xfs))
            if xtran is None:
                xtran = xfs                            # Start with this transform
            else:
                xtran = xtran.compose(xfs)        # Add this transform
            SlTrace.lg("xtran=%s" % xtran)
            SlTrace.lg("    _m:%s" % tran2matrix(xtran))
        return xtran
        '''


    def scale(self):
        """ Return Pt(xscale, yscale) with relative scale from top
        to this component
        """
        comp = self
        comps = []                  # Scale through all containers
        while comp.container is not None:
            comps.insert(0, comp.container)
            comp = comp.container
        
        scale_x = 1.
        scale_y = 1.
        for comp in comps:
            if comp.width is not None:
                scale_x *= comp.width
            if comp.height is not None:
                scale_y *= comp.height
        
        return Pt(scale_x, scale_y)
    
    
    def update_xtran(self):
        """ Create this component's contribution
        to the translation:
          0. get transform for container
          1. translate to origin within container(if one)
          2. scale by size
          3. rotate by rotation(cvt deg to radian)
          4. translate to position within container(if one)
        Omit transformations, having no effect e.g.
                translate(0,0)
                rotation(0)
                scale(1,1)
        Result:
            self.xtran is None if no translation
            self.xtran == translation for this component (before sub parts such as points)
        """
        self.xtran = self.get_xtran(self.container)    # Initialize container's transform
        if self.width is not None or self.height is not None:
            if self.width is None:
                self.width = 1.     # Default scale to full
            if self.height is None:
                self.height = 1.
            xfs = Xscale(self.width, self.height)                       # Scale by comp size
            SlTrace.lg("xfs=%s" % xfs)
            if self.xtran is None:
                self.xtran = xfs                            # Start with this transform
            else:
                self.xtran = self.xtran.compose(xfs)        # Add this transform
        if self.rotation is not None:
            xfr = Xrotate(radians(self.rotation))
            SlTrace.lg("xfr=%s" % xfr)
            if self.xtran is None:
                self.xtran = xfr                                 # Start with this transform
            else:
                self.xtran = self.xtran.compose(xfr)        # Add this transform
        if self.position is not None:
            xft = Xlate(self.position.x, self.position.y)    # Move to origin
            if self.xtran is not None:
                self.xtran = self.xtran.compose(xft)
        SlTrace.lg("xtran=%s" % self.xtran)
    
    def add_components(self, comps):
        """ Add component/list of components
        :comps: one or list of components
        """
        if not isinstance(comps, list):
            comps = [comps]
        for comp in comps:
            self.comps.append(comp)


    def remove_display_objects(self, do_comps=True):
        """ Remove display objects associated with this component
        but not those associated only with components
        :do_comps: True - remove objects of all components
        """
        canvas = self.get_canvas()
        for tg in list(self.canvas_tags.keys()):
            SlTrace.lg("delete tag(%s) in %s" % (tg, self), "display")
            canvas.delete(tg)
            if tg in BlockBlock.tagged_blocks:
                del BlockBlock.tagged_blocks[tg]
            if tg in self.canvas_tags:
                del self.canvas_tags[tg]
        if do_comps and hasattr(self, "comps"):
            for comp in self.comps:
                comp.remove_display_objects(do_comps=True)
    
    def display(self):
        """ Display thing as a list of components
        """
        SlTrace.lg("tag_list: %s" % self.get_tag_list(), "display")
        if not self.visible:
            SlTrace.lg("invisible %s: %s" % (self.ctype, self), "display_invisible")
            self.task_update()    
            return              # Skip if invisible
        
                                # Remove display objects associated with this component

        SlTrace.lg("display %s: %s" % (self.ctype, self), "display")
        if self.ctype == BlockType.COMPOSITE:
            for comp in self.comps:
                comp.display()
                
        else:
            raise SelectError("Unsupported display for %s" % self)


    def task_update(self):
        """ Up Tkinter tasks so display can be seen as soon as possible
        """
        canvas = self.get_canvas()
        if canvas is not None:
            canvas.update_idletasks()
            canvas.update()

    def drag_block(self, delta_x=None, delta_y=None, canvas_coord=False):
        """ Drag selected block, updating block status, and selected infor
        :block: block to move, NOTE: all components will be automatically moved
                                    by the same amount because they are all
                                    defined within this block
        :delta_x: relative x change from current x location in pixels
        :delta_y: relative  y change from current y location in pixels
        :canvas_coord: False - relative to container's coordinates
                        True: relative to top container (canvas) coordinates y going down screen
        """
        self.drag_position(delta_x=delta_x, delta_y=delta_y, canvas_coord=canvas_coord) 
        ###self.display()


    def move_to(self, position=None, canvas_coord=False):
        """ this block, 
                 NOTE: all components will be automatically moved
                        by the same amount because they are all
                        defined within this block
        :position: Pt() destination
        :canvas_coord: False(default) - relative to container's coordinates
                        True: relative to top container (canvas) coordinates y going down screen
        """
        self.set_position(position=position, canvas_coord=canvas_coord) 
        ###self.display()


    def new_type(self, new_type=None, modifier=None, **kwargs):
        """ Create a new object of type "new_type" using all relevant
        characteristics of this block
        :new_type: type of new object (RoadTurn, RoadStrait currently supported)
        :modifier: type modifier e.g. "left", "right"
        """
        from road_strait import RoadStrait
        from road_turn import RoadTurn
        from car_simple import CarSimple
        from block_arrow import BlockArrow
        from block_cross import BlockCross
        track = self.get_road_track()
        if new_type == RoadStrait:    # TFD
            new_block = RoadStrait(track,
                                    position=self.position,
                                    rotation=self.rotation,
                                    origin="road_track", **kwargs)
        elif new_type == RoadTurn:
            arc = 0.
            if modifier == "left":
                arc = 90.
            elif modifier == "right":
                arc = -90.
            new_block = RoadTurn(track,
                                    position=self.position,
                                    rotation=self.rotation,
                                    arc=arc,
                                    origin="road_track", **kwargs)
        elif new_type == CarSimple:
            if modifier == "red":
                base_color = "red"
            elif modifier == "blue":
                base_color = "blue"
            new_block = CarSimple(track,
                                    position=self.position,
                                    rotation=self.rotation,
                                    base_color=base_color,
                                    origin="road_track", **kwargs)
        elif new_type == BlockArrow:            # For direction adjustment selectors
            if modifier == "left":
                rot = self.rotation + 90.
            elif modifier == "right":
                rot = self.rotation - 90.
            else:
                rot = self.rotation
            new_block = BlockArrow(track,
                                    position=self.position,
                                    rotation=rot,
                                    **kwargs)
        elif new_type == BlockCross:            # For direction adjustment selectors
            if modifier == "left":
                rot = self.rotation + 90.
            elif modifier == "right":
                rot = self.rotation - 90.
            else:
                rot = self.rotation
            new_block = BlockCross(track,
                                    position=self.position,
                                    rotation=rot,
                                    **kwargs)
        else:
            raise SelectError("Unsupported type for new_type: %s" % new_type)
        return new_block
    
    
    def dup(self, level=0, max_level=10, keep_id=False, **kwargs):
        """ Duplicate block, replacing any kwargs in destination
        :level: recursive level, in case of recursive definitions
        :max_level: recursive definition limit default: 10
        :keep_id: Keep existing id, used for do/undo memory
        :kwargs: changes to duplicated creation
        """
        duplicate = copy.deepcopy(self)
        for kw in kwargs:
            setattr(duplicate, kw, kwargs[kw])
        if keep_id:
            duplicate.id = self.id
        else:
            duplicate.id = BlockBlock.new_id()
        return duplicate

    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = type(self).__new__(self.__class__)  # skips calling __init__
        new_inst.canvas = self.canvas
        new_inst.container = self.container
        new_inst.color = self.color
        new_inst.state = self.state               # Set by others
        new_inst.ctype = self.ctype
        new_inst.canvas_tags = {}           # tags if any displayed
        new_inst.origin = self.origin
        new_inst.id = self.id
        new_inst.tag = self.tag
        new_inst.canvas = self.canvas
        new_inst.cv_width = self.cv_width
        new_inst.cv_height = self.cv_height
        new_inst.container = self.container
        new_inst.background = self.background
                        
        new_inst.position = self.position
        new_inst.width = self.width
        new_inst.height = self.height
        new_inst.velocity = self.velocity
        new_inst.rotation = self.rotation        
        new_inst.visible = self.visible
        new_inst.xkwargs = self.xkwargs
        
        if hasattr(self, "comps"):
            new_inst.comps = []
            for comp in self.comps:
                comp_copy = copy.deepcopy(comp, memo)
                comp_copy.container = new_inst      # TBD Now: Only works for self referential
                new_inst.comps.append(comp_copy)
        if hasattr(self, "roads"):
            new_inst.roads = {}
            for road in self.roads.values():
                road_copy = road.dup()
                road_copy.container = new_inst      # TBD Now: Only works for self referential
                new_inst.roads[road_copy.id] = road_copy
                
        return new_inst

    
    def drag_position(self, delta_x=None, delta_y=None, canvas_coord=False):
        """ Reposition block position relative to block, using container settings
            It's as if __init__ was called with ...position(Pt(x+delta_x, y+delta_y....)
            :delta_x: change in x
            :delta_y: change in y(down if canvas_coord is True
            :canvas_coord: False (default) container coordinate system
                            True use canvas coordinate system & scale(pixels) y is going down the screen
        """
        position = self.position
        if position is None:
            position = Pt(0,0)
        if not canvas_coord:
            self.position = Pt(position.x+delta_x, position.y+delta_y)
            return
        
        ###abs_cur_pos = self.get_absolute_point(position)
        ###abs_new_pos = Pt(abs_cur_pos.x+delta_x, abs_cur_pos.y+delta_y)
        ###rel_new_pos = self.get_inverse_point(abs_new_pos)
        
        ### HACK based on general scale from current block to top
        scale = self.scale()
        rel_new_pos = Pt(position.x+delta_x/scale.x, position.y-delta_y/scale.y)
        self.position = rel_new_pos


        

    def get_points(self):
        """ Internal points (perimeter)
        :returns: list of internal points
        """
        if not hasattr(self, "points"):
            points = [Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)]       # Boundaries
        else:
            points = self.points
        return points


    def get_position(self):
        """ Get position relative to container
        """
        position = Pt(0,0) if self.position is None else self.position
        return position
    
    def set_position(self, position=None, canvas_coord=False):
        """ Reposition block position 
            It's as if __init__ was called with ...position(position....)
            :canvas_coord: False (default) container coordinate system
                            True use canvas coordinate system & scale(pixels) y is going down the screen
        """
        if position is None:
            raise SelectError("set_position position is None")
        
        if not canvas_coord:
            self.position = position
            return
        
        ###abs_cur_pos = self.get_absolute_point(position)
        ###abs_new_pos = Pt(abs_cur_pos.x+delta_x, abs_cur_pos.y+delta_y)
        ###rel_new_pos = self.get_inverse_point(abs_new_pos)
        
        ### HACK based on general scale from current block to top
        scale = self.scale()
        rel_new_pos = Pt(position.x/scale.x, 1-position.y/scale.y)
        self.position = rel_new_pos

    

    def store_tag(self, tag, keep_old=False):
        """ Store canvas tag.
        Save tag here to facilitate display object removal
        Save tag to be a reference to our block
        :tag: canvas tag to displayed element
        :keep_old: Keep old tags, default delete old tags
        """
        canvas = self.get_canvas()
        if canvas is None:
            return                  # No canvas no display
        
        self.canvas_tags[tag] = tag
                     
        BlockBlock.tagged_blocks[tag] = self
        SlTrace.lg("store_tag(%s) in %s" % (tag, self), "display")   


    def get_canvas_tags(self, level=0, max_level=10):
        """ Get tags from us and levels below us
        :level: current level default 0
        :max_level: maximum number of levels to go
        """
        tags = []
        if level > max_level:
            return []
        
        if hasattr(self, "canvas_tags"):
            tags.extend(self.canvas_tags.keys())
        if hasattr(self, "comps"):
            for comp in self.comps:
                comp_tags = comp.get_canvas_tags(level=level+1)
                tags.extend(comp_tags)
        if hasattr(self, "roads"):
            for road in self.roads.values():
                road_tags = road.get_canvas_tags(level=level+1)
                tags.extend(road_tags)
        return tags


    def rotate(self, rotation=None):
        """ Rotate object by an angle 
        :rotation: rotation(REQUIRED) in degrees
        """
        rot = self.rotation
        if rot is None:
            rot = 0.
        rot += rotation
        if abs(rot) >= 360:
            rot %= 360. 
        self.rotation = rot
        
        
    def tran_points_to_coords(self, points, comp):
        """ Translate points from component to  coordinates
        for Canvas create_poligon
        :points: list of position coordinates
        :comp: expanded position attributes
        """
        pts = []
        for point in self.points:
            pt = self.point_tran(point, comp)
            pts.append(pt)
            
        coords = []
        for pt in pts:
            coords.append(pt[0])
            coords.append(pt[1])


    def tran_point(self, point, comp):
        """ Translate point based on component hierachy
        :point: point in inner most component
        :comp: general component
        """


    def add_to_rot(self, comp):
        """ Adjust possition by relative position of component
        :comp: component containing relative information
        """
        pass        # TBD


    def add_to_vel(self, comp):
        """ Adjust velocity by relative position of component
        :comp: component containing relative information
        """
        pass        # TBD
   
     
    def get_components(self):
        """ Get list of components
        """
        return self.comps

    def move(self, delta, display=True):
        """ Move thing, and all components.
        :delta: change in position
        :display: display updated thing default: True
        """
        for comp in self.get_components():
            comp.move(delta)
        if display:
            comp.display()
        
    
    def coords2pts(self, coords):
        """ Convert Canvas coordinate list to list of
        homcord Pt()
        :coords: list of x1,y1,...xn,yn coordinates
        :returns: list of homcoord Pt()
        """
        canvas = self.get_canvas()
        cv_height = self.get_cv_height()
        height = canvas.winfo_height()
        points = []
        it = iter(coords)
        for x in it:
            y = next(it)
            y = cv_height - y      # down to up
            pt = Pt(x,y) 
            points.append(pt)
        return points
    
    
    def height2pixel(self, h):
        """ Convert height spec(y) to pixels
        :h: height dimension default self.height
        Assumpton top level height is in pixelst
        """
        if h is None:
            h = 1.
        comp = self
        comps = [comp]              
        while comp.container is not None:
            comp = comp.container
            comps.append(comp)
        for cp in comps:
            h *= cp.height
        return h
    
    
    def width2pixel(self, w):
        """ Convert width spec(x) to pixels
        :w: width dimension default self.width
        Assumpton top level width is in pixels
        """
        if w is None:
            w = 1.
        comp = self
        comps = [comp]              
        while comp.container is not None:
            comp = comp.container
            comps.append(comp)
        for cp in comps:
            w *= cp.width
        return w
    
    
    
    def pts2coords(self, pts):
        """ Convert homcoord points to Canvas coordinate list
        :pts: point/list of homcoord Pt()
        :returns: list of x1,y1,....xn,yn coordinates
        """
        if not isinstance(pts,list):
            pts = [pts]
        cv_height = self.get_cv_height()
        coords = []
        for pt in pts:
            x, y = pt.xy
            y = cv_height - y 
            coords.extend([x,y])
        return coords


    def over_rect(self, point, rect=None):
        """ Determine if point is on or inside rectangle
        :point: point to check
        :rect: list of points of rectangle default: self.points
        """
        if rect is None:
            rect = self.points
        
    
    def over_us(self, point=None, coord=None, event=None):
        """ Determine if any point, coordinate, or event is inside our border
            First pass succeeds
            :point: point (Pt)
            :coord: coordinate pair
            :event: mouse event
        """
        if point is not None:
            if self.is_rect:
                return self.over_rect(point)
            
            if self.is_arc:
                return self.over_arc(point)
            
            return False        # Ignore others
        if coord is not None:
            pt = self.coords2pts([coord[0], coord[1]])[0]
            return self.over_us(point=pt)
        
        if event is not None:
            cnv = event.widget
            x,y = float(cnv.canvasx(event.x)), float(cnv.canvasy(event.y))
            pt = self.coords2pts([x,y])[0]
            return self.over_us(point=pt)
        
        return False


        
    
    def front_add_type(self, new_type=None, modifier=None):
        """ Add block_type to front end of block (e.g. road)
        in a way to facilitate road building
            TBD: Possibly changed to determine end of physically connected string
        :new_type: block type to be added
        :modifier:  e.g. "left", "right", ""
        """
        SlTrace.lg("\nblock_block:front_add_type:", "add_block")
        SlTrace.lg("block_block:front_add_type: front_block:%s" % self, "add_block")
        SlTrace.lg("block_block:front_add_type: points:%s" % self.get_absolute_points(), "add_block")
        add_pos1 = self.get_front_addon_position()
        add_pos = self.get_front_addon_position()
        add_rot = self.get_front_addon_rotation()
        if SlTrace.trace("add_block"):
            abs_pos = self.container.get_absolute_point(add_pos)
            SlTrace.lg("block_block:front_add_type: pos:%s(%s) rot:%.0f" % (add_pos, abs_pos, add_rot))
        new_block = self.new_type(new_type, modifier)
        if add_rot != new_block.get_rotation():
            new_block.set_rotation(add_rot)   # Small optimization
        SlTrace.lg("block_block:front_add_type: new_block:%s" % new_block, "add_block")
        SlTrace.lg("block_block:front_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        new_block.move_to(position=add_pos)
        SlTrace.lg("block_block:front_add_type: moved new_block:%s" % new_block, "add_block")
        SlTrace.lg("block_block:front_add_type: points:%s" % new_block.get_absolute_points(), "add_block")
        ###self.set_selected(new_block, keep_old=True)
        return new_block

    
def mkpoint(x,y, color="red", rad=5):
    return BlockBlock.mkpoint(x,y, color=color, rad=rad)

