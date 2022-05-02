
import logging
logger = logging.getLogger(__name__)

import shared.EnvironmentVariables as ev
from .Connection import Connection

from datetime import datetime
from datetime import timedelta
import threading
import queue
import cx_Oracle
import time
import numpy as np
import pandas as pd


class DataFetchDaemon( Connection ):
    def __init__(self) -> None:
        logging.debug("Daemon started")
        self.queue = queue.Queue()
        super().__init__()
        self.__start_fetcher()

    def __collect(self, daily=False) -> None:
        #if not daily: _startTime = ( ( datetime.now() - timedelta( seconds=ev.REFRESH_RATE_NO_NIFI ) ).strftime("%d-%m-%Y %H:%M:%S") ).replace(" ","%20")
        _startTime = ( ( datetime.now().replace(hour=0,minute=0,second=0,microsecond=0) ).strftime("%d-%m-%Y %H:%M:%S") ).replace(" ","%20")
        _format = "csv"
        _endTime = ( datetime.now().strftime("%d-%m-%Y %H:%M:%S") ).replace(" ","%20")
        _mag = 0
        rest = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format={_format}&starttime={_startTime}&endtime={_endTime}&minmagnitude={_mag}"
        logging.debug(f"Making request: {rest}")
        self.data = pd.read_csv( rest )
        self.data = self.data.values.tolist()
        logging.debug(f"ALL DATA COLLECTED (includes other than earthquakes): {len(self.data)}")
        if self.data == []: logging.info("No data to add...")
        self.__dump()

    def __dump(self) -> None:
        for entry in self.data:
            v = [ colVal for colVal in entry ]
            query = \
                f"""INSERT INTO earthquakes 
                (TIME, LATITUDE, LONGITUDE, DEPTH, MAG, MAGTYPE, NST, GAP, DMIN, RMS, NET, ID, UPDATED, PLACE, TYPE, HORIZONTALERROR, DEPTHERROR, MAGERROR, MAGNST, STATUS, LOCATIONSOURCE, MAGSOURCE ) 
                VALUES 
                ('{v[0]}', '{v[1]}', '{v[2]}', '{v[3]}', '{v[4]}', '{v[5]}', '{v[6]}', '{v[7]}', '{v[8]}', '{v[9]}', '{v[10]}', '{v[11]}', '{v[12]}', '{v[13]}', '{v[14]}', '{v[15]}', '{v[16]}', '{v[17]}', '{v[18]}', '{v[19]}', '{v[20]}', '{v[21]}' )"""
            if not super().execute_query( query ): 
                logging.debug(f"Failed to insert event {v[11]}")
                query = \
                    f"""UPDATE earthquakes 
                    SET TIME = '{v[0]}', LATITUDE = '{v[1]}', LONGITUDE = '{v[2]}', DEPTH = '{v[3]}', MAG = '{v[4]}', MAGTYPE = '{v[5]}', NST = '{v[6]}', GAP = '{v[7]}', DMIN = '{v[8]}', RMS = '{v[9]}', NET = '{v[10]}', UPDATED = '{v[12]}', PLACE = '{v[13]}', TYPE = '{v[14]}', HORIZONTALERROR = '{v[15]}', DEPTHERROR = '{v[16]}', MAGERROR = '{v[16]}', MAGNST = '{v[17]}', STATUS = '{v[18]}', LOCATIONSOURCE = '{v[19]}', MAGSOURCE = '{v[20]}' 
                    WHERE ID = '{v[0]}' """
                if not super().execute_query( query ): 
                    logging.debug(f"Failed to update event {v[11]}")
                else: 
                    logging.debug(f"Updated event {v[11]} record")
        commited = super().commit()
        if commited: logging.debug( "Commited changes" )
        else: logging.warning( "Failed to commit changes." )
        return

    def __fetch(self) -> None:
        try:
            self.queue.get(timeout=1)
        except queue.Empty:
            try: 
                logging.debug("Collecting data...")
                self.__collect()
            except cx_Oracle.DatabaseError:
                self.__start_fetcher()
                return
            time.sleep( ev.REFRESH_RATE_NO_NIFI )
            self.__fetch()
            return
        
    def __start_fetcher(self) -> None:
        self.connected = super().open_connection( ev.USER, ev.PASSWORD, ev.DATABASE_DSN )
        #self.__collect( daily=1 )
        logging.debug(f"Connected? {self.connected}")
        if self.connected:
            self.watcher = threading.Thread( target=self.__fetch )
            self.watcher.setName("fetcher")
            self.watcher.setDaemon( True )
            self.watcher.start()
        else: return

    def kill(self) -> None:
        self.queue.put(None)