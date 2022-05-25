
import logging
logger = logging.getLogger(__name__)

import shared.EnvironmentVariables as ev
from tkinter import filedialog, messagebox
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import os

class ParquetManager:
	def __init__(self) -> None:
		return

	def write_to_disk(self, df: pd.DataFrame, event=None) -> bool:
		path = filedialog.asksaveasfilename( defaultextension=".parquet", title="Save view as parquet", filetypes=(("Parquet file", "*.parquet"),) )
		if path != "":
			try: os.makedirs( os.path.dirname( path ) )
			except PermissionError as e: 
				logging.warning(f"Access denied to {path}.\n{e}")
				return 0
			except FileExistsError: pass
			finally: 
				table = pa.Table.from_pandas( df )
				pq.write_table( table, path )
				messagebox.showinfo("Saved!", f"Sucessfully saved file {path}")
				logging.info(f"Saved {path}!")
			return 1
		else: return 0