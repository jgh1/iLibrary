# Assuming your package has a module named 'some_module.py'
# containing a function called 'my_function'
from os.path import join, dirname
import os

import pyodbc
from dotenv import load_dotenv

import iLibrary
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")
conn_str = (
    f"DRIVER={DB_DRIVER};"
    f"SYSTEM={DB_SYSTEM};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD};"
)
conn = pyodbc.connect(conn_str, autocommit=True)
def test_my_function():
    """
    Test case for the get_user_profiles method.
    """
    # 1. Create an instance of the DatabaseManager class
    db_manager = iLibrary.Library(conn)

    # 2. Call the method on the instance, not the class
    # The 'self' argument is now handled automatically
    result = db_manager.getInfoForLibrary(library='AKANSHA231')
    return  result
# You can add more test functions here
# For example, testing a different function from your package

# Simple call to run the test
if __name__ == "__main__":
    print(test_my_function())