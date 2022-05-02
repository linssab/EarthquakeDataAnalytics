
import logging
logger = logging.getLogger(__name__)

import shared.EnvironmentVariables as ev
from tkinter import filedialog
import pandas as pd
import os


class CsvWriter:
	def __init__(self):
		self.data = pd.DataFrame()

	def write_to_disk(self, data: pd.DataFrame, event=None) -> bool:
		self.data = data
		path = filedialog.asksaveasfilename( defaultextension=".csv", title="Save view to CSV", filetypes=(("Comma separated values", "*.csv"),) )
		if path != "":
			try: os.makedirs( os.path.dirname( path ) )
			except PermissionError as e: 
				logging.debug(f"Access denied to {path}.\n{e}")
				return 0
			except FileExistsError: pass
			finally: self.data.to_csv( path, header=True )
			return 1
		else: return 0