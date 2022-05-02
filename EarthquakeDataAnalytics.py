
import logging
import shared.EnvironmentVariables as ev
logging.basicConfig(
    filename="logfile.log",
    filemode="w+",
    level=ev.LOG_LEVEL, 
    format='%(asctime)s:%(funcName)s:%(lineno)d - %(message)s', 
    datefmt='%d-%b-%y %H:%M:%S')
logging.info( "*" * 10 + " Program start " + "*" * 10 )

logging.debug("Loading internal modules...")
from Engine.DataObject import DataObject, geoDataObject
from Engine.EventNumberMonitor import EventNumberMonitor
from Engine.MapView import MapView
from Engine.DataCollector import DataFetchDaemon
from DataIO.CsvWriter import CsvWriter
logging.debug("Done")

import matplotlib.pyplot as plt
from datetime import datetime
import os, sys

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def dummy():
    print("Moo")
    return

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

        self.menu = tk.Menu( self.master, tearoff=False )
        self.menuFileCascade = tk.Menu( self.menu, tearoff=False )
        self.menuFileCascade.add_command( label="Export to *.CSV", 
                                         command= lambda: self.writer.write_to_disk(
                                             self.dataObject.data.iloc[ self.__get_treeview_selection(), : ] ) 
                                         )
        self.menu.add_cascade( label="File", menu=self.menuFileCascade )
        self.master.config( menu=self.menu )

        with open( os.path.join( os.path.dirname(__file__), "shared", "images.b" ), "r" ) as f:
            ICO_SUCCESS = f.readline().split(":")[-1]
            ICO_FAIL = f.readline().split(":")[-1]
        GREEN = tk.PhotoImage( data=ICO_SUCCESS )
        RED = tk.PhotoImage( data=ICO_FAIL )
        self.GREEN = GREEN.subsample( 2 )
        self.RED = RED.subsample( 2 )

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
        self.footer = ttk.Frame( self.master, padding=15 )
        self.footerLeftPane = ttk.Frame( self.footer )
        self.footerRightPane = ttk.Frame( self.footer )
        self.footerStatusLabelTotal = ttk.Label( self.footerLeftPane, text="Number of earthquake records: " )
        self.footerStatusCounterTotal = ttk.Label( self.footerLeftPane, textvariable=self.earthquakeCounter )
        self.footerStatusLabelDaily = ttk.Label( self.footerLeftPane, text="Events recorded today: " )
        self.footerStatusCounterDaily = ttk.Label( self.footerLeftPane, textvariable=self.earthquakeDailyCounter )
        self.showAllinMap = ttk.Button( self.footerRightPane, text="Display in map", command=self.__spawn_map )
        self.clearTreeSelection = ttk.Button( self.footerRightPane, text="Clear selection", command=self.__clear_tree_selection )
        self.connectionStatusFrame = ttk.Frame( self.footerRightPane )
        self.connectionStatusLight = ttk.Label( self.connectionStatusFrame, image=self.RED )
        self.connectionStatusLabel = ttk.Label( self.connectionStatusFrame, text="Connected" )

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
            self.filterButtons.append( 
                ttk.Radiobutton( self.footerRightPane, 
                    text = text, 
                    variable = self.filterSelection,
                    value = text,
                    command=self.__filter ) 
                )
        
        self.header.grid( row=0, sticky="NEWS" )
        self.headerTimeText.grid( sticky="W" )

        self.mainFrame.grid( row=1, padx=10, sticky="NEWS" )
        self.treeFrame.grid( sticky="NEWS" )
        self.treeView.grid( row=0, sticky="NEWS" )
        self.treeXScroll.grid( row=1, sticky="NEWS" )
        self.treeYScroll.grid( row=0, column=1, sticky="NEWS" )

        self.footer.grid( row=2, sticky="NEWS" )
        self.footerLeftPane.grid( row=0, column=0, sticky="WE" )
        self.footerRightPane.grid( row=0, column=1, sticky="WE", padx=(25,0) )
        self.footerStatusLabelTotal.grid( row=0, column=0, sticky="NEWS" )
        self.footerStatusCounterTotal.grid( row=0, column=1, sticky="NSW" )
        self.footerStatusLabelDaily.grid( row=1, column=0, sticky="NEWS" )
        self.footerStatusCounterDaily.grid( row=1, column=1, sticky="NEWS" )

        for (btn, i) in zip( self.filterButtons, range( len(self.filterButtons) ) ):
            btn.grid( row=0, column=i, padx=(10,0), sticky="NEWS" )

        self.showAllinMap.grid( row=0, column=self.footerRightPane.grid_size()[0]+1, padx=(10,0), sticky="NEWS" )
        self.clearTreeSelection.grid( row=0, column=self.footerRightPane.grid_size()[0]+1, sticky="NEWS" )
        self.connectionStatusFrame.grid( row=0, column=self.footerRightPane.grid_size()[0]+1, sticky="E" )
        self.connectionStatusLabel.grid( row=0, column=0, sticky="E" )
        self.connectionStatusLight.grid( row=0, column=1, sticky="E" )

        self.master.columnconfigure( 0, weight=1 )
        self.master.rowconfigure( 1, weight=1 )
        self.mainFrame.columnconfigure( 0, weight=1 )
        self.mainFrame.rowconfigure( 0, weight=1 )
        self.treeFrame.columnconfigure( 0, weight=1 )
        self.treeFrame.columnconfigure( 1, weight=0 )
        self.treeFrame.rowconfigure( 0, weight=1 )
        self.treeFrame.rowconfigure( 1, weight=0 )
        self.footer.columnconfigure( 0, weight=0 )
        self.footer.columnconfigure( 1, weight=1 )
        for col in range( self.footerRightPane.grid_size()[0]-1 ):
            self.footerRightPane.columnconfigure( col, weight=0 )
        self.footerRightPane.columnconfigure( self.footerRightPane.grid_size()[0]-1, weight=1 )

        self.treeView.bind( "<Double-Button-1>", self.__spawn_map )

        self.master.update_idletasks()
        self.KILL = 0
        self.master.after( 1000, self.__update_clock ) # TODO: Make it a thread
        self.master.minsize( width=self.master.winfo_width(), height=self.master.winfo_height()+200 )
        self.master.after( 200, self.master.iconbitmap( os.path.join( os.path.dirname(__file__), "shared", "icon.ico" ) ) )

    def __launch_clock(self) -> None:
        return

    def __update_clock(self) -> None:
        global clockId
        if ev.TRIGGER: 
            messagebox.showwarning("New events!", 
                                   f"We have received new event(s)!")
            self.__populate_with_data()
        if ev.CONNECTED: self.connectionStatusLight.config( image=self.GREEN )
        else: self.connectionStatusLight.config( image=self.RED )
        self.currentTimeUtc.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.headerTimeText.update_idletasks()
        clockId = self.master.after(1000, self.__update_clock)

    def __start(self) -> None:
        self.__start_watchdogs()
        self.writer = CsvWriter()
        self.master.mainloop()

    def __start_watchdogs(self) -> None:
        if not ev.NIFI: self.dataFetcher = DataFetchDaemon()
        self.eventNumberMonitor = EventNumberMonitor()

    def __kill(self) -> None:
        if not ev.NIFI: self.dataFetcher.kill()
        self.master.after_cancel( clockId )
        self.master.update_idletasks()
        self.master.destroy()
        sys.exit(1)

    def __get_treeview_selection(self) -> list:
        idx = []
        self.treeView.update_idletasks()
        selectedItems = list( self.treeView.selection() )
        if selectedItems == []: itemIds = [ self.treeView.item( item )["values"][-1] for item in self.treeView.get_children() ]
        else: itemIds = [ self.treeView.item( iid )["values"][-1] for iid in selectedItems ]
        for itemId in itemIds:
            idx.append( self.dataObject.data.index[ self.dataObject.data["ID"] == itemId ][0] )
        return idx

    def __spawn_map(self, event=None) -> None:
        if event is None:
            idx = self.__get_treeview_selection()
            if idx == []: return
            else: 
                MapView( geoDataObject( self.dataObject.data.iloc[ idx, : ] ) )
        else: # double-click
            event.widget.update_idletasks()
            curItem = self.treeView.item( self.treeView.selection() )
            try: 
                if curItem["values"][-1] != "": like = curItem["values"][-1]
            except IndexError: return
            idx = self.dataObject.data.index[ self.dataObject.data["ID"] == like ].tolist()
            if idx == []: return
            MapView( geoDataObject( self.dataObject.data.iloc[idx] ) )

    def __clear_tree_selection(self, event=None) -> None:
        for i in self.treeView.selection():
            self.treeView.selection_remove( i )

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
