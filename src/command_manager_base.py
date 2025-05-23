# command_manager_base.py
"""
Base level command manager, without drawing_controler/user_module
move manager morphed from Java ExtendedModeler: EMBCCommandManager
"""
from select_trace import SlTrace
from command_stack import CommandStack

class CommandManagerBase:
    """
    current command
    command_stack - commands executed
    undo stack - commands undone
    """
    cmd_no = 0      # To be unique command number/id
    
    def __init__(self):
        self.current_command = None
        self.command_stack = CommandStack()
        self.undo_stack = CommandStack()


    def command_stack_str(self):
        """ Provide printable string containing current
        command stack
        """
        return str(self.command_stack)

    def command_undo_stack_str(self):
        """ Provide printable string containing current
        command undo stack
        """
        return str(self.undo_stack)
    
    def displayPrint(self, msg="", trace=None):
        SlTrace.lg(f"do_cmd({msg} display TBD", "execute")

    def selectPrint(self, msg="", trace=None):
        '''
        SlTrace.lg("do_cmd(%s) select TBD"  % (self.action), "execute")
        '''

    def do_cmd(self, cmd):
        """ Do command, saving if successful and can undo or repeat
        """
        return cmd.do_cmd()
        
    """
     * Check if command stack is empty
    """
    
    def is_empty(self):
        return self.command_stack.is_empty()


    """
     * Check if undo command stack is empty
    """
    def is_undo_empty(self):
        return self.undo_stack.is_empty()

    
    def last_command(self):
        """ Peek at last command
        :returns: CommandBase
        """
        if self.command_stack.is_empty():
            return None
        
        return self.command_stack.peek()
    
    def last_visible_command(self):
        """ Peek at last visible command
        :returns: Command
        """
        cs_size = self.command_stack.size()
        for sidx in range(cs_size):
            cmd = self.command_stack.element_at(sidx)
            if cmd.is_visible():
                return cmd
            
        return None

    
    def last_undo_command(self):
        """ Peek at undo command
        :returns: Command
        """
        return self.undo_stack.peek()

    def next_cmd_no(self):
        CommandManagerBase.cmd_no = CommandManagerBase.cmd_no + 1
        return CommandManagerBase.cmd_no

    """
     * Check if can redo this command
    """
    def can_redo(self):
        if self.undo_stack.is_empty():
            return False
        cmd = self.last_undo_command()
        return cmd.can_redo()


    """
     * Check if can repeat this command
    """
    def can_repeat(self):
        if self.command_stack.is_empty():
            return False
        cmd = self.last_command()
        return cmd.can_repeat()


    """
     * Check if can undo this command
    """
    def can_undo(self):
        if self.command_stack.is_empty():
            return False
        cmd = self.last_command()
        if not cmd.can_undo():
            return False        # Can't undo
        return True


    


    
    """
     * Check point command state
     * by pushing command, which upon undo, will create current state
    """
    def check_point(self):
        SlTrace.lg("check_point", "execute")
        '''TBD
        try:
            cmd = EMBCommand.check_pointCmd()
            self.undo_stack.push(cmd)
        except EMBlockError as e:
            # TODO Auto-generated catch block
            e.printStackTrace()
        '''


    def pop_undo_cmd(self):
        """ Pop command off command_stack
        :returns: command from top of command_stack
                    None if command_stack is empty
        """
        if not self.command_stack.is_empty():
            return self.command_stack.pop()
        
        return None    
    
    """
     * Undo if possible
     * command and select stack modifications are done through EMBCommand functions
    """
    def undo(self):
        SlTrace.lg("undo", "execute")
        if (not self.can_undo()):
            SlTrace.lg("Can't undo")
            return False

        cmd = self.command_stack.pop()
        res = cmd.undo()
        if res:
            self.undo_stack.push(cmd)
        return res

    def undo_all(self):
        """ Undo all commands in stack
        """
        while self.command_stack.size() > 0:
            self.undo()

    """
     * Re-execute the most recently undone command
    """
    def redo(self):
        SlTrace.lg("redo", "execute")
        if (not self.can_redo()):
            SlTrace.lg("Can't redo")
            return False

        cmd = self.undo_stack.pop()
        res = cmd.execute()
        if res:
            self.command_stack.push(cmd)
        return res

    def get_repeat(self):
        """ Get command copy which would, if executed,
        "repeat" last command
        :returns command which would repeat
            or None if none 
        """       
        if (not self.can_repeat()):
            return None

        cmd = self.last_visible_command()
        if cmd is None:
            return None
        
        cmd_last = self.last_command()
        cmd = cmd.use_locale(cmd_last)  # Update for changes
        
        return cmd.get_repeat()


    def repeat(self):        
        """ Re execute the most recently done visible
        command
        """
        SlTrace.lg("repeat", "execute")
        cmd = self.get_repeat()
        if cmd is None:
            SlTrace.lg("Can't repeat")
            return False

        return cmd.repeat()


    """
     * Save command for undo/redo...
    """
    
    def save_cmd(self, bcmd):
        self.command_stack.push(bcmd)

    def add(self, bcmd):
        """ Add command alias for save_cmd
        :bcmd: command (CommandBase)
        """
        self.save_cmd(bcmd)
    


    def any_selected(self):
        select = self.get_selected()
        return len(select) > 0


    
    def get_current_command(self):
        """ get most recent command, if one
        :returns: current command, if one, else None
        """
        if self.command_stack.is_empty():
            return None
        
        return self.command_stack.peek()


    """
     * Get previous command, if any
     * Return previous command, if one else
     * return current command if one else
     * return None
    """
    def get_prev_commad(self):
        if self.command_stack.is_empty():
            return None
        if self.command_stack.size() < 2:
            return self.command_stack.peek()
        return self.command_stack.element_at(1)


    """
     * Get previously executed command's selection
    """
    def get_prev_selected(self):
        prev_cmd = self.get_prev_commad()
        if prev_cmd is None:
            return []
        return prev_cmd.new_select


    def get_move_no(self):
        return 0        # TBD added/overridden if needed

    def get_prev_move_no(self):
        return 0        # TBD added/overridden if needed
    
    
    """
     * Get previously executed command's selected block
     * Use current command if command stack only has one 
    """
    def get_prev_selected_marker(self):
        prev_select = self.get_prev_selected()
        if len(prev_select)== 0:
            return None
        return prev_select[0]


    
    """
     * Get currently selected blocks
    """
    def get_selected_markers(self):
        select = self.get_selected()
        return select

    
    """
     * Get currently selected
    """
    def get_selected(self):
        cmd = self.get_current_command()
        if cmd is None:
            return []        # Empty when none
        
        return cmd.new_select

    """
     * Get currently selected block if any
    """
    def get_selected_marker(self):
        select = self.get_selected()
        if len(select) == 0:
            return None
        return select[0]

    
    
    """
     * Check select stack
    """
    def select_is_empty(self):
        return len(self.get_selected()) == 0

    
    
    def select_pop(self):
        SlTrace.lg("No select stack")
        return self.get_selected()

    

    """
     * Set selection
    """
    def set_selected(self, select):
        cmd = self.get_current_command()
        cmd.set_select(select)



    


    

    """
     * Print command stack
    """
    def cmd_stack_print(self, tag, trace=None):
        max_print = 5
        stack_str = ""
        if self.command_stack.is_empty():
            SlTrace.lg(f"{tag} self.command_stack: Empty", trace)
            return

        cmds = self.command_stack.get_cmds()
        nprint = max_print
        if SlTrace.trace("verbose"):
            nprint = 9999
        for cmd in cmds:
            if stack_str != "":
                stack_str += "\n"
            stack_str +=     "   " + str(cmd)

        SlTrace.lg(f"{tag} cmd Stack: {self.command_stack.size()}\n"
                   f" {stack_str}", trace)

    

if __name__ == "__main__":
    import os
    SlTrace.lg(f"{os.path.basename(__file__)} Selftest")