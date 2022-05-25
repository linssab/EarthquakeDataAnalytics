
import shared.EnvironmentVariables as ev
from .Connection import Connection
import pandas as pd
import geopandas
import copy

class geoDataObject:
    def __init__(self, entry: pd.DataFrame) -> None:
        df = copy.deepcopy( entry )
        self.data = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy( df["LONGITUDE"], df["LATITUDE"] ) )


class DataObject( Connection ):
    def __init__(self) -> None:
        super().__init__()
        self.connected = super().open_connection( ev.USER, ev.PASSWORD, ev.DATABASE_DSN )
        self.data = pd.DataFrame()
        return None

    def execute_sql( self, query: str ) -> pd.DataFrame:
        """ Executes an SQL query to the connected database. 
        Returns None if the query fails. """
        if self.connected: 
            self.data = super().sql_queryl( query )
            self.__convert_data_types()
        return self.data

    def __convert_data_types(self) -> None:   
        if hasattr( self.data, "TIME" ): self.data["TIME"] = pd.to_datetime(self.data["TIME"], infer_datetime_format=True)
        if hasattr( self.data, "LATITUDE" ): self.data["LATITUDE"] = pd.to_numeric(self.data["LATITUDE"], errors='coerce')
        if hasattr( self.data, "LONGITUDE" ): self.data["LONGITUDE"] = pd.to_numeric(self.data["LONGITUDE"], errors='coerce')
        if hasattr( self.data, "DEPTH" ): self.data["DEPTH"] = pd.to_numeric(self.data["DEPTH"], errors='coerce')
        if hasattr( self.data, "MAG" ): self.data["MAG"] = pd.to_numeric(self.data["MAG"], errors='coerce')
        if hasattr( self.data, "NST" ): self.data["NST"] = pd.to_numeric(self.data["NST"], errors='coerce')
        if hasattr( self.data, "GAP" ): self.data["GAP"] = pd.to_numeric(self.data["GAP"], errors='coerce')
        if hasattr( self.data, "DMIN" ): self.data["DMIN"] = pd.to_numeric(self.data["DMIN"], errors='coerce')
        if hasattr( self.data, "RMS" ): self.data["RMS"] = pd.to_numeric(self.data["RMS"], errors='coerce')
        if hasattr( self.data, "UPDATED" ): self.data["UPDATED"] = pd.to_datetime(self.data["UPDATED"], infer_datetime_format=True)
        if hasattr( self.data, "HORIZONTALERROR" ): self.data["HORIZONTALERROR"] = pd.to_numeric(self.data["HORIZONTALERROR"], errors='coerce')
        if hasattr( self.data, "DEPTHERROR" ): self.data["DEPTHERROR"] = pd.to_numeric(self.data["DEPTHERROR"], errors='coerce')
        if hasattr( self.data, "MAGERROR" ): self.data["MAGERROR"] = pd.to_numeric(self.data["MAGERROR"], errors='coerce')
        if hasattr( self.data, "MAGNST" ): self.data["MAGNST"] = pd.to_numeric(self.data["MAGNST"], errors='coerce')
        return None