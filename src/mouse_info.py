# mouse_motion.py
from select_trace import SlTrace
from select_error import SelectError

class MouseInfo:
    """ Mouse motion info
    """
    def __init__(self, event=None, x_coord=None, y_coord=None, x_coord_prev=None,  y_coord_prev=None):
        """
        :event: Record most recent event
        :x_coord: x-coordinate on canvas
        :y_coord: y-coordinate
        :x_coord_prev: previous mouse x_coord
        :y_coord_prev: previous y_coord
        """
        if x_coord is None:
            raise SelectError("MouseInfo when x_coord is None")
        self.event = event
        self.x_coord = x_coord
        self.y_coord = y_coord
        if x_coord_prev is None:
            x_coord_prev = x_coord
        self.x_coord_prev = x_coord_prev
        if y_coord_prev is None:
            y_coord_prev = y_coord
        self.y_coord_prev = y_coord_prev
