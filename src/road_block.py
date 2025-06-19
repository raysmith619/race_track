# road_block.py        
"""
Basis of a road network
Uses BlockBlock parts
"""
from enum import Enum
import copy
from homcoord import *


from select_trace import SlTrace
from select_error import SelectError

from block_block import BlockBlock, BlockType
from block_text import BlockText

class RoadType(Enum):
    COMPOSITE = 1
    STRAIGHT = 2
    TURN = 3
    CROSS = 4

class SurfaceType(Enum):
    DEFAULT = 1
    ASFAULT = 2
    CONCRETE = 3
    DIRT = 4
    GRASS = 5


   
class RoadBlock(BlockBlock):
    """
    A Part of a road 
    which can be used to construct a road layout
    """
    
            
    def __init__(self,
                container,
                road_type=RoadType.COMPOSITE,
                road_width=None,
                road_length=None,
                surface=None,
                median_width=.03,
                median_x=.5,
                off_edge=.02,
                edge_width=.0,
                front_road=None,
                back_road=None,
                road_width_feet=45,
                marked=False,
                **kwargs):
        """ Setup Road object
        :container: Road object containing this object
                      OR
                    RoadTrack 
        :road_type: container type defalut:COMPOSITE
        :road_width:  road's width as fraction of width
                        default: track's road_width
        :road_length:  road's length as fraction of width
                        default: track's road_length
        :median_width: width of median line
        :median_x:    position of median line within width
        :off_edge:    spacing of edge lines off edge
        :edge_width: width of edge lines
        :front_road: road connected in front, if one default: None
        :back_road: road for which this is a front_road
        :marked: Set true for tracking / debugging
        """
        SlTrace.lg("\nRoadBlock: %s %s container: %s" % (road_type, self, container), "block create")
        self.marked = marked    
        self.road_type = road_type
        self.road_width = road_width 
        self.road_length = road_length
        self.median_width = median_width
        self.median_x = median_x
        self.off_edge = off_edge
        self.edge_width = edge_width
        if surface is None and container is not None:
            surface = container.surface
        self.surface = surface
        self.front_road = front_road
        self.back_road = back_road
        super().__init__(container=container, **kwargs)        
        self.highlight_tag = None


    def __deepcopy__(self, memo):
        """ Hook to avoid deep copy where not appropriate
        """
        new_inst = super().__deepcopy__(memo)
        new_inst.road_width = self.road_width
        new_inst.road_length = self.road_length
        new_inst.surface = self.surface
        new_inst.front_road = self.front_road       # shallow        
        new_inst.back_road = self.back_road       # shallow
        new_inst.marked = self.marked               # ??? Should this be copied or reset?      
        return new_inst
        
        
    
    def add_components(self, comps):
        """ Add component/list of components
        :comps: one or list of components
        """
        if not isinstance(comps, list):
            comps = [comps]
        for comp in comps:
            self.comps.append(comp)

    
    def display(self):
        """ Display thing as a list of components
        """
        if not self.visible:
            return              # Skip if invisible
        
        SlTrace.lg("display %s: %s" % (self.get_tag_list(), self), "display")
        for comp in self.comps:
            comp.display()
        
        self.task_update()

    def mark(self, color="red"):
        self.marked = True
        for comp in self.comps:
            comp.xkwargs = {'fill' : 'pink'}
        mark_text = BlockText(container=self, position=(Pt(-.5,-.5)), text="%d" % self.id)
        self.comps.append(mark_text)
        self.display()

    def highlight(self, color="green"):
        """ Highlight block temporarly
        :color: base color
        """
        if self.highlight_tag is not None:
            self.canvas.delete(self.highlight_tag)
        coords = self.get_perimeter_coords()
        xkwargs = {'fill': color}
        self.highlight_tag = self.get_canvas().create_polygon(coords, **xkwargs)
        
                
    def get_road_track(self):
        top = self.get_top_container()
        return top

    def get_race_track(self):
        road_track = self.get_road_track()
        race_track = road_track.get_race_track()
        return race_track
 
    def get_road_width_feet(self):
        return self.get_road_track().get_road_width_feet()

    def get_road_width(self):
        """ Get road width in fraction of container
        """
        if self.road_width is None:
            return self.container.get_road_width()
        
        return self.road_width
        

    def get_road_length(self):
        """ Get road length in fraction of container
        """
        if self.road_length is None:
            return self.container.get_road_length()
        
        return self.road_length


    def get_back_road(self):
        """ Get previous road in chain, if one
        :returns: previous road, None if none
        """
        return self.back_road


    def get_front_road(self, allow_close=True):
        """ Get next road in chain, if one
        If no immediate chain is found, check for close one
        and add it if found.
        :returns: next road, None if none
        """
        if self.front_road is not None:
            if SlTrace.trace("front_road"):
                SlTrace.lg("%s direct link to %s " % (self, self.front_road))
            return self.front_road
        
        if not allow_close:
            SlTrace.lg("%s don't check for close" % (self))
            return None         # Don't allow close checking
    
        race_track = self.get_race_track()
        if race_track is None:
            return None
        
        add_pos_coords = self.get_infront_coords()
        if SlTrace.trace("front_road"):
            SlTrace.lg("%s coords:%s" % (self, add_pos_coords))
        front_road = race_track.get_entry_at(*add_pos_coords,
                                                   entry_type="road")
        if front_road is None:
            SlTrace.lg("get_front_road(%s) finds nothing in front at: %s" % (self, add_pos_coords))
            SlTrace.lg(" %s coords: %s " % (self, self.get_absolute_points()))
            self.mkpoint(add_pos_coords[0], add_pos_coords[1], "orange")
            front_road2 = race_track.get_entry_at(*add_pos_coords,
                                                   entry_type="road")
            return front_road2
        else:
            if SlTrace.trace("front_road"):
                SlTrace.lg("%s close to %s - linked" % (self, front_road))
            if front_road.id == self.id:
                SlTrace.lg("%s is 'close' to itself" % (self))
                SlTrace.lg(" %s pts: %s %s " % (self, self.get_absolute_points(), self.get_coords()))
                inside_pts = self.get_points()
                for inside_pt in inside_pts:
                    rel_pt = self.get_relative_point(inside_pt)         # In container's reference
                    abs_pt = self.get_absolute_point(rel_pt)
                    coords = self.pts2coords(abs_pt)
                    SlTrace.lg("%s inside_pt %s rel_pt:%s abs_pt:%s coords:%s"
                                % (self, inside_pt, rel_pt, abs_pt, coords))
                SlTrace.lg(f"Don't link to self:{self.id = }")
                return None
                
            self.link_roads(front_road) # link roads
        return front_road
    
    
    def get_modifier(self):
        """ Get modifier for road
        :returns: modifier string
        """
        return ""
                

    def get_turn_speed(self):
        """ Get reduced speed for turns
        """
        return 10           #MPH
    
    def get_straight_acc(self):
        """ Get acceleration on straight away
        """
        return 10


    def get_position_at(self, dist=0., side_dist=0.):
        """ Get road position at distance within the road segment
        approximate by a linear interperlation of start and end
        :dist: fractional distance through the road segment
        :side_dist: Adjust return position by this distance,
                 as a fraction of the width, from left edge
        """
        end_position = self.get_front_addon_position()
        start_position = self.get_position()
        chg_position = (end_position-start_position)
        leng_dist = self.get_length_dist()
        fract_dist = dist/leng_dist
        chg_x = chg_position.x * fract_dist
        chg_y = chg_position.y * fract_dist
        position = Pt(start_position.x+chg_x, start_position.y+chg_y)
        if side_dist != 0.:
            rotation = self.get_rotation_at(dist=dist)
            norm_rot = rotation - 90.           # Rotate 90deg towards right side
            theta = radians(norm_rot)
            sd = side_dist*self.get_width()
            ###sd = side_dist                      # HACK
            side_pt_polar = Polar(sd, theta)
            side_pt = side_pt_polar.toCartesian()
            ### HACK
            ep = .001
            norm_rot %= 360.
            if norm_rot < 0:
                norm_rot += 360.
            if norm_rot >= 0 and norm_rot < 90.-ep:         # road left
                side_pt = Pt(0,sd)
            elif norm_rot >= 90 and norm_rot < 180.-ep:     # road down
                side_pt = Pt(-sd,0)
            elif norm_rot >= 180 and norm_rot < 270.-ep:    # road right
                side_pt = Pt(0,-sd)                     
            elif norm_rot >= 270.-ep:                       # road up
                side_pt = Pt(sd,0)
            ### HACK END
                
            position += side_pt
        return position


    def get_rotation_at(self, dist=0.):
        """ Get road rotation at distance within the road segment
        approximate by a linear interperlation of start and end
        :dist: fractional distance through the road segment
        """
        end_rotation = self.get_front_addon_rotation()
        start_rotation = self.get_rotation()
        leng_dist = self.get_length_dist()
        rotation = start_rotation + abs(end_rotation-start_rotation)* dist/leng_dist
        return rotation
    
    def get_road_rotation(self):
        """ Get road rotation in degrees
        Adds in  container or track rotation if any
        :returns: None if no rotation
        """
        if self.container is not None:
            rot = self.container.get_road_rotation()
            rot2 = self.rotation
            if rot2 is None:
                rot2 = rot
            return rot2
        
        rot = self.track.get_road_rotation()
        rot2 = self.rotation
        if rot2 is None:
            rot2 = rot
        return rot2

    def chg_in_front_rotation(self, new_rotation):
        """ Get change in rotation from current direction to new direction
        :new_rotation: direction our addon to a new block rotation
        :returns: rotation between 0 and 360 to get new_rotation
        """
        return (new_rotation-self.get_front_addon_rotation())%360

    def get_front_addon_rotation(self):
        """ Get rotation for a forward "addon" block
        :returns: rotation of addon block in containers reference
                    None if no rotation, treated as 0. deg
        """
        return  self.get_rotation()

    def is_front_of(self, road, rotation_diff=.0001, position_diff=.0001):
        """ Determine if we are placed so as to be exactly in front of road
        :road: candidate back road
        """
        road_front_rotation = self.get_rotation()
        road_front_position = self.get_position()
        
        road_back_rotation = road.get_front_addon_rotation()
        road_back_position = road.get_front_addon_position()
        if abs(road_front_rotation-road_back_rotation) > rotation_diff:
            return False
        
        if road_front_position.dist(road_back_position) > position_diff:
            return False
        
        return True

    def link_roads(self, road):
        """ link this road with road in front of it
        :road:  link road as our front road and us as road's back_road
        """
        self.front_road = road
        road.back_road = self
    

    def out_road_cmd(self, file=None):
        """ Write out road command text
        :file:  oputput file handle
        """
        out_str = "road(id=%d" % self.id
        out_str = self.wrap_out_str(out_str, ", classtype=%s" % self.__class__.__name__)
        if hasattr(self, "modifier") and self.modifier is not None and self.modifier != "":
            out_str = self.wrap_out_str(out_str, ", modifier=%s" % self.get_modifier())
        if self.position is not None:
            out_str = self.wrap_out_str(out_str, ", position=Pt%s" % self.position)
        if self.rotation is not None:
            out_str = self.wrap_out_str(out_str, ", rotation=%f" % self.rotation)
        if self.width is not None:
            out_str = self.wrap_out_str(out_str, ", width=%f" % self.width)
        if self.height is not None:
            out_str = self.wrap_out_str(out_str, ", height=%f" % self.height)
        if hasattr(self, "arc") and self.arc is not None:
            out_str = self.wrap_out_str(out_str, ", arc=%f" % self.arc)
        if self.front_road is not None:
            out_str = self.wrap_out_str(out_str, ", front_road=%d" % self.front_road.id)
        if self.back_road is not None:
            out_str = self.wrap_out_str(out_str, ", back_road=%d" % self.back_road.id)
        out_str += ")"
        print(out_str, file=file)
        
        
    def get_road_surface(self):
        return self.track.get_road_surface()




    
    def show_add_on_selects(self, add_on_types=None, **kwargs):
        """ Dispplay areas which, by mouse selection, can be added to track.
        :returns: list of selection block objects
        """
        selects = []
        if add_on_types is None:
            add_on_types = type(self)
        if not isinstance(add_on_types, list):
            add_on_types = [add_on_types]
        add_pos = self.get_front_addon_position()
        add_rot = self.get_front_addon_rotation()
        if len(kwargs) == 0:
            kwargs = {'background' : 'pink'}
            kwargs['xkwargs'] = {'fill' : 'pink'}
        for add_on_type in add_on_types:
            new_block = self.new_type(add_on_type, **kwargs)
            if add_rot != new_block.get_rotation():
                new_block.set_rotation(add_rot)   # Small optimization
            new_block.move_to(position=add_pos)
            new_block.display()
            selects.append(new_block)
        
        return selects
        