"""
A software that analyzes the vibration of the region of interest in video.
Plot the line chart of POI relative motivation for both vertical and horizontal.
Export the csv file of POI coordination.

Existing Bug: Select ROI invalid after the first select.
"""

__author__ = "Duxxi"
__copyright__ = "Copyright 2019, The VibrationDetection Project"
__license__ = "GPL"
__version__ = "1.0.0"


from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from analyze_program import *

# tOPTIONS = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'MOSSE', 'CSRT']
# pOPTIONS = ["Central Point", "Left-Top Point", "Right-Top Point", "Right-Bottom Point", "Left-Bottom Point"]
# gOPTIONS = ['Vertical', 'Horizontal']
tOPTIONS = list(TRACKER_TYPES.keys())
pOPTIONS = list(POI_TYPES.values())
gOPTIONS = list(GRAPH_TYPES.values())


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.video = None
        self.title("VD")
        self.minsize(200, 300)
        self.wm_iconbitmap('icon.ico')
        self.filename = None
        self.labelFrame = ttk.LabelFrame(self, text="Open File")
        self.labelFrame.grid(column=0, row=0, padx=20, ipady=5)
        self.file_button()
        self.analyze_button()
        self.generate_button()
        self.menu()

    def file_button(self):
        fbutton = ttk.Button(self.labelFrame, text="Browse A File", command=self.file_dialog)
        fbutton.grid(column=0, row=1, ipadx=20, padx=30)

    def menu(self):
        """
        Tracker/Point/Graph DropDown Menu Config
        """
        self.tracker_var = StringVar(self)
        self.point_var = StringVar(self)
        self.graph_var = StringVar(self)
        self.tracker_var.set(tOPTIONS[0])
        self.point_var.set(pOPTIONS[0])
        self.graph_var.set(gOPTIONS[0])
        tracker_drop_menu = OptionMenu(self, self.tracker_var, *tOPTIONS)
        point_drop_menu = OptionMenu(self, self.point_var, *pOPTIONS)
        graph_drop_menu = OptionMenu(self, self.graph_var, *gOPTIONS)
        tracker_drop_menu.grid(column=0, row=1, ipadx=20, pady=5)
        point_drop_menu.grid(column=0, row=2, ipadx=20, pady=5)
        graph_drop_menu.grid(column=0, row=3, ipadx=20, pady=5)

    def analyze_button(self):
        abutton = ttk.Button(text="Analyze", command=self.analyze)
        abutton.grid(column=0, row=4, ipadx=20, pady=10)

    def generate_button(self):
        gbutton = ttk.Button(text="Generate", command=self.export)
        gbutton.grid(column=0, row=5, ipadx=20)

    def analyze(self):
        """
        Analyzing main entrance
        """
        if not self.filename:
            messagebox.showinfo("Error", "Please Select a Valid Video First")
        if self.filename:
            print(self.tracker_var.get())
            self.video = VideoInit(self.filename, tOPTIONS.index(self.tracker_var.get()))
            self.video.run_analyze(str(pOPTIONS.index(self.point_var.get())), str(gOPTIONS.index(self.graph_var.get())))

    def export(self):
        if not self.video:
            messagebox.showinfo("Error", "Please Analyze First")
        else:
            self.video.points.export_data()
            messagebox.showinfo("Complete", "Export Complete")

    def file_dialog(self):
        """
        FileDialog Config, select video file and show path
        """
        self.filename = filedialog.askopenfilename(initialdir="/", title="Select A File", filetype=
        (("mp4 files", "*.mp4"), ("avi files", "*.avi"), ("all files", "*.*")))
        label = ttk.Label(self.labelFrame, text="")
        label.grid(column=0, row=0)
        label.configure(text=self.filename)


root = Root()
root.mainloop()