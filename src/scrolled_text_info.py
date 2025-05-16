#scrolled_text_info.py
# Make scrolled_text.py into a class 
#  Importing required modules

import tkinter as tk
import tkinter.scrolledtext as st

class ScrolledTextInfo:
    def __init__(self, win=None, title=None, label=None, text=None,
                 xpos=None, ypos=None):
        """ Display text in scrolled text
        :win: based window
        :title: window title
        :label: optional label text
        :text: to display
        :xpos: text window screen x-position
                default: no change
        :ypos: text window screen x-position
                default: no change
        """
        if win is None:
            # Creating tkinter window
            win = tk.Tk()
            if xpos is not None:
                geo = f"+{xpos}+{ypos}"
                win.geometry(geo)
                
        self.win = win
        
        if title:
            win.title(title)

        if label:
            # Title Label
            tk.Label(win, 
                    text = label, 
                    font = ("Times New Roman", 15), 
                    background = 'green', 
                    foreground = "white").pack()

        # Creating scrolled text area
        # widget with Read only by
        # disabling the state
        text_area = st.ScrolledText(win,
                                    width = 60, 
                                    height = 10, 
                                    font = ("Times New Roman",
                                            20))

        text_area.pack(fill=tk.BOTH, expand=True)

        # Inserting Text which is read only
        text_area.insert(tk.INSERT, text)
        # Making the text read only
        text_area.configure(state ='disabled')

if __name__ == '__main__':
    root = tk.Tk()
    
    text = """\
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

    sti = ScrolledTextInfo(root, title="ScrolledTextInfo Test", text=text)

    sti.win.mainloop()