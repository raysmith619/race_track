# block_commands.py
"""
block file command support  for car race game for python file Execution
"""
import sys
import traceback

from select_error import SelectError
from select_trace import SlTrace
from _ast import arg

bC = None               # Global reference, set by CommandFile
class BlockCommands:
    """ The hook from commands expressed via python command files to 
    the frame worker
    """
    @classmethod
    def get_cmds(cls):
        return bC
    
        
    def __init__(self, play_control, debugging=False, src_file_path=None):
        """
        :play_control: control for action commands
        :src_file_path: file path of source
        :debugging: True - Just testing no command execution enabled
        """
        global bC                       # Static link to dots commands
        self.play_control = play_control
        self.src_file_path = src_file_path
        self.debugging = debugging
        self.debugging_res = True       # Default debugging
        self.new_file = True
        bC = self                       # set link to dots commands


    def get_src_file_path(self):
        """ Get current source file path
        """
        return self.src_file_path
        
    def ck(self, *args, **kwargs):
        """ Check command.
        Executed at beginning of each language command
        Check with hasattr because attribute is only
        created when called with links
        :returns: True if should SKIP rest of this cmd processing
        """
        if bC is None or not hasattr(bC, "command_stream"):
            raise SelectError("Missing required command_stream")
        
        if (self.is_src_lst() or self.is_stx_lst()
                or self.is_stepping()):
            if self.new_file:
                self.src_line_prev = -1
                with open(self.get_src_file_path()) as f:
                    self.src_lines = f.readlines()
                    self.new_file = False
            """ List portion of source file, after previous(index) to and including
            the line in the source file found in the stack
            """
            ###etype, evalue, tb = sys.exc_info()
            ###tbs = traceback.extract_tb(tb)
            tbs = traceback.extract_stack()
            src_lineno = None       # set if found
            src_tbfr = None         # stack frame for src
            src_tbfr_fun = None     # with called function name
            for tbfr in tbs:         # skip bottom (in dots_commands.py)
                if tbfr.filename == self.get_src_file_path():
                    src_lineno = tbfr.lineno
                    src_tbfr = tbfr
                    src_tbfr_fun = None     # Clear if we get another
                    continue
                if src_tbfr is not None and src_tbfr_fun is None:
                    src_tbfr_fun = tbfr
            if src_lineno is not None:
                src_line_index = src_lineno-1
                if src_line_index < self.src_line_prev:
                    self.src_line_prev = src_line_index # looping?
                for idx in range(self.src_line_prev+1, src_line_index+1):
                    if idx >= len(self.src_lines):
                        break
                    lineno = idx + 1
                    src_line = self.src_lines[idx].rstrip()
                    if self.is_src_lst():
                        SlTrace.lg("   %4d: %s" % (lineno, src_line))
                        self.src_line_prev = idx        # Update as printed
            if self.is_stx_lst():
                if src_tbfr_fun is not None:
                    fun_name = src_tbfr_fun.name
                    fun_str = None
                    for arg in args:
                        if fun_str is None:
                            fun_str = fun_name + "(" + repr(arg)
                        else:
                            fun_str += ", " + repr(arg)
                    if fun_str is None:
                        fun_str = fun_name + "("
                    for kw in kwargs:
                        arg = kwargs[kw]
                        fun_str += ", " + kw + "=" + repr(arg)
                    fun_str += ")"
                    SlTrace.lg("         SCMD: %s" % fun_str)
        
        if self.is_step():
            self.wait_for_step()    # At target, wait for step/continue
            
        if self.is_to_line(cur_lineno=src_lineno):
            self.wait_for_step()   # At target line, wait for step/continue
                     
        if self.is_debugging():
            return True            # Skip action because debugging                return False                # No reason to skip rest, do it

        return False        # No reason not to continue
    
    
    def is_debugging(self):
        """ Check if debugging, if so we can disregard execution
        """
        if self.debugging:
            return True         # Ignore
        
        return False
    
    
    def wait_for_step(self):
        return False
        
        
    def is_step(self):
        return False
        
        
    def is_to_line(self, cur_lineno=None, src_lines=None):
        if src_lines is None:
            src_lines = self.src_lines
        return False
    
    
    def is_src_lst(self):
        """ Are we listing source lines?
        """
        return False

    def is_stx_lst(self):
        """ Are we listing executing commands?
        """
        return False
    
    
    def ck_res(self):
        """ debugging ck return
        """
        return self.debugging_res

    def set_debugging(self, debugging = True):
        """ Set to debug command language, elimitting
        action requiring full game
        """
        self.debugging = debugging
        BlockCommands.play_control = None    # Suppress ck eror
            
    
    """
    Process (Execute) standard python/Jython file as a domain (e.g. blocks) specific command file
    """
    def procFilePy(self, inFile):
        inPath = SlTrace.getSourcePath(inFile, req=False)
        if inPath is None:
            self.error("inFile({} was not found".format(inFile))
            return False
        with open(inPath) as f:
            try:
                code = compile(f.read(), inPath, 'exec')
            except Exception as e:
                tbstr = traceback.extract_stack()
                SlTrace.lg("Compile Error in %s\n    %s)"
                        % (inPath, str(e)))
                return False
            try:
                exec(code)
            except Exception as e:
                etype, evalue, tb = sys.exc_info()
                tbs = traceback.extract_tb(tb)
                SlTrace.lg("Execution Error in %s\n%s)"
                        % (inPath, str(e)))
                inner_cmds = False
                for tbfr in tbs:         # skip bottom (in dots_commands.py)
                    tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                    if not inner_cmds and tbfr.filename.endswith("dots_commands.py"):
                        inner_cmds = True
                        SlTrace.lg("    --------------------")         # show bottom (in dots_commands.py)
                    SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
                return False
            self.eof = True             # Consider at end of file
        return True
        
    
    """
    Block commands
    """
    
    def lg(self, *args, **kwargs):
        self.ck(*args, **kwargs)  # No debugging
        return SlTrace.lg(*args, **kwargs)

    def car(self, **kwargs):
        """ Add car to track
        :id: relative id number for car
            Shifted if current id is less than this id
            If shifted the resulting id creates a new base which is added
            to subsequent ids
        :classtype: type of road e.g. CarSimple
        :modifier: road modifier e.g. "left", "right"
        """
        if self.play_control is None:
            raise SelectError("No play control")
        return self.play_control.car(**kwargs)


    def road(self, **kwargs):
        """ Add road to track
        :id: relative id number for road
            Shifted if current id is less than this id
            If shifted the resulting id creates a new base which is added
            to subsequent ids
        :classtype: type of car e.g. CarSimple
        :modifier: road modifier e.g. "left", "right"
        :front_road: id for forward link
        :back_road: id for backward link
        """
        if self.play_control is None:
            raise SelectError("No play control")
        return self.play_control.road(**kwargs)
    
    
bC = BlockCommands.get_cmds()
"""
language commands
"""
def lg(*args, **kwargs):
    return bC.lg(*args, **kwargs)

def road(**kwargs):
    return bC.road(**kwargs)

def car(**kwargs):
    return bC.car(**kwargs)
