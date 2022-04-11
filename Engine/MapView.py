

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import font as tkFont

import os
import numpy as np
import geopandas as gpd
import matplotlib
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk

from .DataObject import geoDataObject


class NavigationToolbar(NavigationToolbar2Tk):
    toolitems = (
    ('Home', 'Reset original view', 'home', 'home'),
    ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
    ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
    ('Save', 'Save the figure', 'filesave', 'save_figure')
  )


class MapView:
    def __init__(self, geoDataObject: geoDataObject):
        self.master = tk.Toplevel()
        self.master.protocol("WM_DELETE_WINDOW", self.__wipe_plot)
        self.master.attributes("-alpha",0.0)
        self.geoDataObject = geoDataObject
        self.alt = False
        self.master.bind("<Alt_L>",self.__altOn)
        self.master.bind("<KeyRelease-Alt_L>",self.__altOff)
        self.master.bind("<Return>",self.__maximize)
        self.master.title("Plot")

        self.master.minsize(width=600,height=480)
        self.master.configure(bg='white')
        self.master.resizable(True,True) 
        self.plot_font = {'fontname':'Arial','fontsize':14}

        self.lw = 3
        self.master.tagged = None
        self.menubar = tk.Menu(self.master, tearoff=0)
        self.options = tk.Menu(self.menubar, tearoff=0)
        self.upper = tk.Canvas(self.master)
        self.upper.config( bg='white' )
        self.lower = ttk.Frame( self.master, height=35 )

        self.upper.pack(side=tk.TOP, expand=True, fill=tk.BOTH, padx=(16,16), pady=(16,16))
        self.lower.pack(side=tk.BOTTOM, anchor="n", fill=tk.BOTH, expand=0)
        
        self.figure = Figure(figsize=(16,9))
        self.plot = self.figure.add_subplot(111)
        self.plot.grid(which='both',axis='both')
        self.plot.grid(color="black", ls="--", lw=0.5)
        self.plot.axis('On')
        self.canvas = FigureCanvasTkAgg(self.figure, self.upper)
        self.mplCanvas = self.canvas.get_tk_widget()
        self.mplCanvas.pack( fill=tk.BOTH, anchor="nw", expand=True )
        self.toolbar = NavigationToolbar(self.canvas,self.lower)
        self.toolbar.update()
        self.canvas._tkcanvas.pack()

        self.plot.spines["top"].set_color("black")
        self.plot.spines["top"].set_linewidth(2)
        self.plot.spines["bottom"].set_color("black")
        self.plot.spines["bottom"].set_linewidth(2)
        self.plot.spines["left"].set_color("black")
        self.plot.spines["left"].set_linewidth(2)
        self.plot.spines["right"].set_color("black")
        self.plot.spines["right"].set_linewidth(2)
        self.plot.set_aspect('equal')

        self.master.after(100,self.master.attributes,"-alpha",1.0)
        self.__draw_image()
        self.canvas.draw()
    
    def __altOn(self,e=""):
        self.alt = True

    def __altOff(self,e=""):
        self.alt = False

    def __maximize(self,e=""):
        if self.alt == False: return
        elif self.master.state()=="zoomed": self.master.state("normal")
        else: self.master.state("zoomed")
    
    def __draw_image(self) -> None:
        self.worldmap = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
        self.worldmap.plot(color="lightgrey", ax=self.plot)
        x = self.geoDataObject.data["LONGITUDE"]
        y = self.geoDataObject.data["LATITUDE"]
        z = self.geoDataObject.data["MAG"]
        vmax = max(z)
        vmin = 0
        self.plot.scatter(x, y, s=20*z, c=z, alpha=0.6, cmap='hot_r', vmin=vmin, vmax=vmax)
        self.plot.set_xlim([-180, 180])
        self.plot.set_ylim([-90, 90])
        self.plot.set_xlabel("Longitude")
        divider = make_axes_locatable( self.plot )
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.figure.colorbar(plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax), cmap="hot_r"), cax=cax, label="Magnitude")
        self.plot.set_title("Earthquake events")

    def __wipe_plot(self):
        self.plot.clear()
        self.figure.clf()
        self.master.destroy()
