
import logging
import shared.EnvironmentVariables as ev
logger = logging.getLogger(__name__)
print(ev.ORACLE_CLIENT_PATH)
import cx_Oracle
import pandas as pd
import pandas.io.sql as psql
cx_Oracle.init_oracle_client( lib_dir=ev.ORACLE_CLIENT_PATH )

class Connection:  
    def __init__(self):
        self.connection = None
        self.cursor = None
        return
        
    def open_connection(self, user: str, password: str, dbPath: str) -> int:
        try: 
            self.connection = cx_Oracle.connect(
                user=user, 
                password=password,
                dsn=dbPath)
            self.cursor = self.connection.cursor()
            logging.debug(f"Conected to {user}/{password}@{dbPath}")
            ev.NUMBER_OF_RECORDS = self.count_records()
            ev.CONNECTED = True
        except Exception as e: 
            logging.warning(f"Failed to connect to {user}/{password}@{dbPath}")
            ev.CONNECTED = False
            return 0
        return 1

    def count_records(self) -> int:
        """ Return an integer with the number of records in the connection database """
        sql = "SELECT count(*) FROM EARTHQUAKES e WHERE e.type='earthquake'"
        self.cursor.execute( sql )
        return [row for row in self.cursor][0][0]

    def __query(self, query: str) -> list:
        """ retuns a list of tuples with the specified query results, where each tuple is one row """
        self.cursor.execute( query )
        return [row for row in self.cursor]

    def get_headers(self) -> list:
        query = """
            SELECT column_name
            FROM USER_TAB_COLUMNS
            WHERE table_name = 'EARTHQUAKES'
            """
        self.cursor.execute( query )
        return [row for row in self.cursor]

    def commit(self) -> bool:
        try: self.connection.commit()
        except: return 0
        return 1

    def execute_query(self, query: str) -> bool:
        try: self.cursor.execute( query )
        except Exception as e:
            return 0
        return 1

    def sql_queryl(self, query: str) -> pd.DataFrame:
        """ returns a Pandas dataframe object """
        results = pd.DataFrame()
        try: 
            results = psql.read_sql( query , con=self.connection )
        except Exception as e: 
            logging.error(f"{e}")
        return results