#text_info.py 15May2025  crs, From Stackoverflow/Mike Driscoll

import tkinter as tk
import tkinter.scrolledtext as st

class TextInfo(object):

    def __init__(self, parent, title = None,
                 textfield = 'a text field', label = None):

        self.top = tk.Toplevel(parent)
        self.parent = parent
        self.title = title
        self.textfield = textfield

        # set window title
        if title:
            self.top.title(title)
            
        # Title Label
        tk.Label(parent, 
                text = title, 
                font = ("Times New Roman", 15), 
                background = 'green', 
                foreground = "white").grid(column = 0,
                                            row = 0)

        # add label if given
        if label:
            tk.Label(self.top, text=title).grid(row=0)

        # Creating scrolled text area
        # widget with Read only by
        # disabling the state
        self.text_area = st.ScrolledText(parent, 
                                      width = 40, 
                                      height = 10, 
                                      font = ("Times New Roman",
                                              15))

        self.text_area.grid(column = 0, pady = 10, padx = 10)
        # Inserting Text which is read only
        self.text_area.insert(tk.INSERT, textfield)
        
        # Making the text read only
        self.text_area.configure(state ='disabled')

        # Placing cursor in the text area
        self.text_area.focus()

        # create the ok button
        b = tk.Button(self.top, text="OK", command=self.ok)
        b.grid(row=2)

    def ok(self):
        self.top.destroy()
        
        
if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    title = "General Help"
    label = None
    prompt = """
    This program facilitates the creation of simple
    two-dimentional race tracks, each supporting
    the racing of a number of two-dimentional cars.
    
    The racing is very simple.  The fun, so far, is
    the creation of various closed path tracks and
    the placement of an arbitrary number of cars on
    each.
    
    The mouse can select a road track from the bin
    below.  Then click the desired position on the
    green track area.
    
    The Position Parts window supports modifying
    the the road part on the track.
    """
    prompt   = """\
This is a scrolledtext widget to make tkinter text read only.
Hi
Geeks !!!
Geeks !!!
Geeks !!! 
Geeks !!!
Geeks !!!
Geeks !!!
Geeks !!!
"""
    TextInfo(root, title=title, textfield=prompt, label=label)  
    root.mainloop()
    