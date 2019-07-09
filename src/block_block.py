# block_block.py        

from enum import Enum
import copy
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError
from wx.lib.sized_controls import border
from _hashlib import new


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
      rotation    rotation (degrees counter clockwise) relative to container
                  0 = strait up
      velocity    velocity: x,y / second
    internal:
      base_xtran - homogenous transform when needed
    When a BlockBlock moves/rotates The components move/rotate accordingly
    """
    id = 0
    tagged_blocks = {}      # Displayed blocks, by canvas tag
    id_blocks = {}          # Blocks by block id

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
                
        
            
    def __init__(self,
                 canvas=None,
                 cv_width=None,
                 cv_height=None,
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
        self.container = container
        if background is None:
            background = "white"
        self.background = background
        SlTrace.lg("\nBlockBlock[%d]:%s %s %s container: %s" % (self.id, tag, ctype, self, container))
        SlTrace.lg("tag_list: %s" % self.get_tag_list(), "block_create")    
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
                height *= self.get_cv_height()            
                        
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
                points = [Pt(0,0), Pt(0,1), Pt(1,1), Pt(1,0)]       # Boundaries
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
    

    def get_relative_points(self, points=None):
        """ Get points based on current block position
        :points: base point/points to translate
                defajlt: self.points
        :returns: list of translated points
                e.g. if default gives points as transformed
                by base transform
        """
        if points is None:
            points = self.points
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


    def get_top_left(self):
        """ Get top left corner in container's  terms
        so container can use next_entry(position=previous_entry.get_top_left()...) to place next_entry on
        the top left of previous entry.
        """
        tlc = self.get_relative_point(Pt(0,1))
        container = self.container if self.container is not None else self
        SlTrace.lg("get_top_left %s = %s(%s)" % (self.get_tag_list(), tlc, self.container.get_absolute_point(tlc)))
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
        SlTrace.lg("get_canvas: top:%s selects:%s" % (top, top.selects))
        return top.canvas
    
    
    def get_cv_height(self):
        """ Return canvas height (or projected height)
        """
        top = self.get_top_container()
        cv_height = top.cv_height
        if cv_height is None:
            cv_height = 600
        return cv_height
    
    
    def get_cv_width(self):
        """ Return canvas width (or projected width)
        """
        top = self.get_top_container()
        if not hasattr(top, "cv_width"):
            raise SelectError("has no cv_width")
        return top.cv_width


    def has_canvas(self):
        """ Determine if this object has a canvas
        """        
        top = self.get_top_container()
        if hasattr(top, "canvas"):
            return True
        
        return False

               
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


    def remove_display_objects(self):
        """ Remove display objects associated with this component
        but not those associated only with components
        """
        canvas = self.get_canvas()
        for tg in list(self.canvas_tags.keys()):
            SlTrace.lg("delete tag(%s) in %s" % (tg, self), "display")
            canvas.delete(tg)
            del BlockBlock.tagged_blocks[tg]
            del self.canvas_tags[tg]
       
    
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

    def dup(self):
        """ Duplicate block, replacing any kwargs
        """
        duplicate = copy.deepcopy(self)
        duplicate.id = BlockBlock.new_id()
        return duplicate

    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = type(self).__new__(self.__class__)  # skips calling __init__
        new_inst.canvas = self.canvas
        new_inst.container = self.container
        new_inst.state = self.state               # Set by others

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
                new_inst.comps.append(copy.deepcopy(comp, memo))
        if hasattr(self, "roads"):
            new_inst.roads = []
            for comp in self.roads:
                new_inst.roads.append(copy.deepcopy(comp, memo))
                
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

    
    def is_selected(self):
        """ Check if selected or any in the container chain is
        selected
        """
        top = self.get_top_container()
        return top.is_selected(self)

    

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
            for comp in self.roads:
                comp_tags = comp.get_canvas_tags(level=level+1)
                tags.extend(comp_tags)
        return tags


    def rotate(self, rotation=None):
        """ Rotate object by an angle 
        :rotation: rotation(REQUIRED) in degrees
        """
        rot = self.rotation
        if rot is None:
            rot = 0.
        rot += rotation
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
        for x,y in coords:
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
        :pts: list of homcoord Pt()
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
     