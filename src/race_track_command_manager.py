#race_track_command_manager.py  18May2025 crs
""" RaceTrack version of command manager
"""
from command_manager_base import CommandManagerBase
from race_track_command import RaceTrackCommand

class RaceTrackCommandManager(CommandManagerBase):
    """ manage race track commands
    """
    def __init__(self, user_control):
        """ Manage race track commands
        :user_control: RaceTrack control
        """
        super().__init__()
        self.user_control = user_control

    def undo(self):
        """ Undo, removing any display_only commands preceeding standard commands
        """
        while (cmd := self.pop_display_only()) is not None:
            cmd.undo()      # Just undo display
            
        return super().undo()
    
    def pop_display_only(self):
        """ Retrieve display_only cmd, iff one on command_stack, removing from stack
        :returns: display_only command if one, else None
        """
        cmd = self.last_command()
        if cmd is None:
            return None     # No commands
            
        if cmd.display_only:
            cmd = self.pop_command()
            return cmd
        
        return None

    def pop_command(self):
        """ Pop command off command_stack
        :returns: command from top of command_stack
        """
        if self.command_stack.is_empty():
            return None
        
        return self.command_stack.pop()    