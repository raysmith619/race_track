#race_track_command.py  18May2025  crs
""" Race Track command
"""
from select_trace import SlTrace
from select_error import SelectError
from command_base import CommandBase

class RaceTrackCommand(CommandBase):
    
    def __init__(self, entries, grouped=True, type="add_entry", display_only=False):
        """ contain command for possible undo/redo
        :entries: one/list of road/cars to be added
        :grouped: Add to current group
        :type: command type default: add_entry
        :display_only: True if display only, ignored for undo/redo
                        default: False
        """
        super().__init__(type)
        self.entries = entries
        self.grouped = grouped
        self.type = type
        self.action = type
        self.display_only = display_only

    def __str__(self):
        st = ""
        if self.display_only:
            st += "  DISPLAY"
        st += f" {self.type}"
        if isinstance(self.entries, list):
            st += f" LIST:"
            for entry in self.entries:
                st += f" {entry}"
        else:
            st += f" {self.entries}"
        return st
        
    def execute(self):
        """ Execute command, with no change to stack
        """
        if self.type == "add_entry":
           res = self.command_manager.user_control.add_entry_cmd(self)
        elif self.type == "remove_entry":
           res =  self.command_manager.user_control.remove_entry_cmd(self)
        else:
            raise SelectError(f"Unrecognized racetrack command type:"
                              f" {self.type}")
            return False
        
        return res
    
      
    def undo(self):
        """
        Remove the effects of the most recently done command
          1. remove command from commandStack
          2. add command to undoStack
          3. reverse changes caused by the command
          4. return true iff could undo
        Non destructive execution of command
        """
        cmd = None
        try:
            new_cmd = RaceTrackCommand(self.entries)
        except:
            SlTrace.lg("Undo failure")
            return False
        
        if self.type == "add_entry":
            new_cmd.type = "remove_entry"
        elif self.type == "remove_entry":
            new_cmd.type = "add_entry"
        new_cmd.entries = self.entries
        new_cmd.grouped = self.grouped
        
        res = new_cmd.execute()
        return res
   