
import shared.EnvironmentVariables as ev
from Engine.DataObject import DataObject, geoDataObject
from Engine.EventNumberMonitor import EventNumberMonitor
from Engine.MapView import MapView

import matplotlib.pyplot as plt
from datetime import datetime
import os, sys
import sklearn

import tkinter as tk
from tkinter import ttk


def make_query( start: str, end: str) -> str:
    return \
        "SELECT "    +\
            "e.time, e.latitude, e.longitude, e.depth, e.mag, e.magerror, e.place, e.status, e.id "  +\
        "FROM "  +\
            "EARTHQUAKES e " +\
        "WHERE " +\
           "e.type = 'earthquake' " +\
        "AND "   +\
            "e.time "    +\
        "BETWEEN "   +\
            f"'{start}' "  +\
        "AND "   +\
            f"'{end}'"

class GUI:
    def __init__(self) -> None:
        self.master = tk.Tk()
        self.master.protocol("WM_DELETE_WINDOW", self.__kill)
        self.master.title("Earthquake monitor")
        self.dataObject = DataObject()
        self.__build_widgets()
        self.__start()

    def __build_widgets(self) -> None:
        self.headers = {
            "TIME": {"size":220, "minwidth":190}, 
            "LATITUDE":{"size":125, "minwidth":90}, 
            "LONGITUDE":{"size":125, "minwidth":90}, 
            "DEPTH":{"size":125, "minwidth":60}, 
            "MAG":{"size":125, "minwidth":60}, 
            "MAGERROR":{"size":125, "minwidth":60}, 
            "PLACE":{"size":350, "minwidth":200}, 
            "STATUS":{"size":125, "minwidth":80},
            "ID":{"size":100, "minwidth":100}
            }

        self.earthquakeCounter = tk.IntVar()
        self.earthquakeDailyCounter = tk.IntVar()
        self.currentTimeUtc = tk.StringVar()
        self.filterSelection = tk.StringVar()
        self.filterSelection.set("Show all")
        self.earthquakeCounter.set(ev.NUMBER_OF_RECORDS)
        self.earthquakeDailyCounter.set(0)
        self.currentTimeUtc.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        self.filterValues = {
            "Show all": ["ALL",""],
            "Show reviewed only" : ["STATUS", "reviewed"],
            "Magnitudes above 2.5" : ["MAG", 2.5] }

        self.mainFrame = ttk.LabelFrame( self.master, text="Events of today", padding=10 )
        self.treeFrame = ttk.Frame( self.mainFrame, padding=10, width=600 )
        self.header = ttk.Frame( self.master, padding=10 )
        self.headerTimeText = ttk.Label( self.header, textvariable=self.currentTimeUtc )
        self.footer = ttk.Frame( self.master, padding=10 )
        self.footerLeftPane = ttk.Frame( self.footer )
        self.footerRightPane = ttk.Frame( self.footer )
        self.footerStatusLabelTotal = ttk.Label( self.footerLeftPane, text="Number of earthquake records: " )
        self.footerStatusCounterTotal = ttk.Label( self.footerLeftPane, textvariable=self.earthquakeCounter )
        self.footerStatusLabelDaily = ttk.Label( self.footerLeftPane, text="Events recorded today: " )
        self.footerStatusCounterDaily = ttk.Label( self.footerLeftPane, textvariable=self.earthquakeDailyCounter )
        self.showAllinMap = ttk.Button( self.footerRightPane, text="Display in map", command=self.__spawn_map )

        self.treeView = ttk.Treeview( self.treeFrame, columns=list(self.headers.keys()), show="headings" )
        for head in self.headers.keys(): 
            self.treeView.heading( head, text=head, anchor="w" )
            self.treeView.column( head, width=self.headers[head]["size"], minwidth=self.headers[head]["minwidth"], stretch=False )
        self.treeXScroll = ttk.Scrollbar( self.treeFrame, orient=tk.HORIZONTAL )
        self.treeXScroll.configure( command=self.treeView.xview )
        self.treeYScroll = ttk.Scrollbar( self.treeFrame, orient=tk.VERTICAL )
        self.treeYScroll.configure( command=self.treeView.yview )
        self.treeView.configure( xscrollcommand=self.treeXScroll.set )
        self.treeView.configure( yscrollcommand=self.treeYScroll.set )

        self.filterButtons = []
        for (text, value) in self.filterValues.items():
            self.filterButtons.append( ttk.Radiobutton( self.footerRightPane, text = text, variable = self.filterSelection,
               value = text,
               command=self.__filter ) )
        
        self.header.grid( row=0, sticky="NEWS" )
        self.headerTimeText.grid( sticky="W" )

        self.mainFrame.grid( row=1, padx=10, sticky="NEWS" )
        self.treeFrame.grid( sticky="NEWS" )
        self.treeView.grid( row=0, sticky="NEWS" )
        self.treeXScroll.grid( row=1, sticky="NEWS" )
        self.treeYScroll.grid( row=0, column=1, sticky="NEWS" )

        self.footer.grid( row=2, sticky="NEWS" )
        self.footerLeftPane.grid( row=0, column=0, sticky="W" )
        self.footerRightPane.grid( row=0, column=1, sticky="E", padx=(25,0) )
        self.footerStatusLabelTotal.grid( row=0, column=0, sticky="NEWS" )
        self.footerStatusCounterTotal.grid( row=0, column=1, sticky="NSW" )
        self.footerStatusLabelDaily.grid( row=1, column=0, sticky="NEWS" )
        self.footerStatusCounterDaily.grid( row=1, column=1, sticky="NEWS" )

        for (btn, i) in zip( self.filterButtons, range( len(self.filterButtons) ) ):
            btn.grid( row=0, column=i, padx=(10,0) )

        self.showAllinMap.grid( row=0, column=self.footerRightPane.grid_size()[0]+1 )
        
        self.master.columnconfigure( 0, weight=1 )
        self.master.rowconfigure( 1, weight=1 )
        self.mainFrame.columnconfigure( 0, weight=1 )
        self.mainFrame.rowconfigure( 0, weight=1 )
        self.treeFrame.columnconfigure( 0, weight=1 )
        self.treeFrame.columnconfigure( 1, weight=0 )
        self.treeFrame.rowconfigure( 0, weight=1 )
        self.treeFrame.rowconfigure( 1, weight=0 )
        self.footerLeftPane.columnconfigure( 1, weight=1 )

        self.treeView.bind( "<Double-Button-1>", self.__spawn_map )

        self.master.update_idletasks()
        self.master.after( 1000, self.__update_clock )
        self.master.minsize( width=self.master.winfo_width(), height=self.master.winfo_height()+200 )
        self.master.after( 200, self.master.iconbitmap( os.path.join( os.path.dirname(__file__), "shared", "icon.ico" ) ) )

    def __update_clock(self) -> None:
        if ev.TRIGGER: self.__populate_with_data()
        self.currentTimeUtc.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.headerTimeText.update_idletasks()
        self.master.after(1000, self.__update_clock)

    def __start(self) -> None:
        self.__start_watchdog()
        self.master.mainloop()

    def __start_watchdog(self) -> None:
        self.eventNumberMonitor = EventNumberMonitor( )

    def __kill(self) -> None:
        self.master.destroy()

    def __spawn_map(self, event=None) -> None:
        if event is None: 
            MapView( geoDataObject( self.dataObject.data ) )
        else:
            event.widget.update_idletasks()
            curItem = self.treeView.item( self.treeView.selection() )
            if curItem["values"][-1] != "": like = curItem["values"][-1]
            idx = self.dataObject.data.index[ self.dataObject.data["ID"] == like ].tolist()
            print( curItem, idx, like )
            MapView( geoDataObject( self.dataObject.data.iloc[idx] ) )

    def __filter(self) -> None:
        head, string = self.filterValues[self.filterSelection.get()]
        if head == "ALL": alwaysAdd = True
        else: alwaysAdd = False
        self.treeView.delete( *self.treeView.get_children() )

        for index in range( len( self.dataObject.data ) ):
            values = []
            add = False
            for column in self.dataObject.data:
                if column == head:
                   if self.dataObject.data[column][index] >= string: add = True
                if isinstance( self.dataObject.data[column][index], float): values.append( round( self.dataObject.data[column][index], 5 ) )
                else: values.append(self.dataObject.data[column][index])
            if add or alwaysAdd: 
                self.treeView.insert('', tk.END, values=values )
                add = False
        self.treeView.update_idletasks()            
        return None

    def __populate_with_data(self) -> None:
        self.treeView.delete( *self.treeView.get_children() )
        query = make_query( 
            datetime.now().strftime('%Y-%m-%dT00:00:00'),
            datetime.now().strftime('%Y-%m-%dT%H:%M:%S') )
        self.dataObject.execute_sql( query )
        self.__filter()
        self.treeView.update_idletasks()            
        self.earthquakeCounter.set(ev.NUMBER_OF_RECORDS)
        self.earthquakeDailyCounter.set( len( self.dataObject.data ) )
        ev.TRIGGER = False


if __name__.endswith("__main__"):
    
    GUI()

    """
    query = make_query( 
            datetime.now().strftime('%Y-%m-%dT00:00:00'), 
            datetime.now().strftime("%Y-%M-%DT%H:%M:%S") )

    data = DataObject()
    data.execute_sql( query )
    
    results = data.data
    print( results.describe() )

    results.hist(bins=50, figsize=(20,15))
    plt.show()

    results.plot(kind="scatter", x="LONGITUDE", y="LATITUDE", s=results["MAG"]*2, alpha=0.4, color="red")
    plt.show()
    """