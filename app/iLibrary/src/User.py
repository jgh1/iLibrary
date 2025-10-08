from os.path import join
import paramiko
import pyodbc
import json
from datetime import datetime, date
from decimal import Decimal
from .getUserInfoForUser import *

class User(getUserInfoForUser):
    """
        A class to manage User on IBMi System

        It provides methods to connect to the system via pyodbc for SQL and
        paramiko for SFTP transfers.
    """

    # ------------------------------------------------------
    # __init__ - initzialise the class
    # ------------------------------------------------------
    def __init__(self, db_user: str, db_password: str, db_host: str, db_driver: str):
        """
        Initializes the class attributes for a database connection.
        The actual connection is established in the __enter__ method.

        Args:
            db_user (str): The user ID for the database connection.
            db_password (str): The password for the database user.
            db_host (str): The system/host name for the database connection.
            db_driver (str): The ODBC driver to be used.
        """
        self.db_user = db_user
        self.db_host = db_host
        self.db_driver = db_driver
        self.db_password = db_password

    # ------------------------------------------------------
    # __enter__ - enter to the class
    # ------------------------------------------------------
    def __enter__(self) -> 'User':
        """
        Establishes the database connection when entering a 'with' block.
        """
        try:
            conn_str = (
                f"DRIVER={self.db_driver};"
                f"SYSTEM={self.db_host};"
                f"UID={self.db_user};"
                f"PWD={self.db_password};"
            )
            self.conn = pyodbc.connect(conn_str, autocommit=True)
            return f'Moin {self.db_user}, this Function is Still in work :)'
            #return self
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            print(f"Database connection failed with error: {sqlstate}")
            raise

    # ------------------------------------------------------
    # __exit__ - leave the class
    # ------------------------------------------------------
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Closes the database connection when exiting a 'with' block.
        This method is called automatically, even if an error occurred.
        """
        self.iclose()

    # ------------------------------------------------------
    # iClose - close connection
    # ------------------------------------------------------
    def iclose(self):
        """
        A helper method to close the connection, also useful for manual closure.
        """
        if self.conn and not self.conn.closed:
            self.conn.close()
            pass