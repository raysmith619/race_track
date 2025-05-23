#race_way_cmd_mgr.py    18May2025  crs
""" Manage commands - simple version
"""
from select_trace import SlTrace
from command_manager import CommandManager

class RaceWayCmdMgr(CommandManager):
    def __init__(self, race_track):
        """ Setup manager
        :race_track: reference to track
        """
        super().__init__(self)  # Implement drawing_controller here
        


if __name__ == '__main__':
    from race_track import RaceTrack
    
    SlTrace(f'Self test for :{__name__}')
    rT = RaceTrack()
    rwcmd_mgr = RaceWayCmdMgr()
    SlTrace("End Test")