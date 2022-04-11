
import shared.EnvironmentVariables as ev
from .Connection import Connection
import cx_Oracle
from tkinter import messagebox
import threading
import time

STARTING_EVENTS = ev.NUMBER_OF_RECORDS

class EventNumberMonitor( Connection ):

    def __init__(self) -> None:
        super().__init__()
        self.__start_watcher()
        return None

    def __watch(self) -> None:
        global STARTING_EVENTS
        try: ev.NUMBER_OF_RECORDS = super().count_records()
        except cx_Oracle.DatabaseError:
            self.__start_watcher()
            return None
        if ev.NUMBER_OF_RECORDS != STARTING_EVENTS:
            messagebox.showwarning("New events!", 
                                   f"We have received {ev.NUMBER_OF_RECORDS - STARTING_EVENTS} new event(s)!")
            STARTING_EVENTS = ev.NUMBER_OF_RECORDS
            ev.TRIGGER = True
        else: pass
        time.sleep(30)
        self.__watch()
        return None

    def __start_watcher(self) -> None:
        super().open_connection( ev.USER, ev.PASSWORD, ev.DATABASE_DSN )
        self.watcher = threading.Thread( target=self.__watch )
        self.watcher.setName("watcher")
        self.watcher.setDaemon( True )
        self.watcher.start()