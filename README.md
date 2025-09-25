## iLibrary
  
This class provides methods to connect to the system via pyodbc for SQL and paramiko for SFTP transfers.  
  
### Modules  required
  ---
* json  
* os  
* paramiko  
* pyodbc  
  
### Class Library  
  ---
A class to manage libraries and files on an IBM i system. It provides methods to connect to the system via pyodbc for SQL and paramiko for SFTP transfers.  
  
### Methods  
  ---
#### __enter__(self) -> 'Library'  
---  
Establishes the database connection when entering a `with` block.  
  
#### __exit__(self, exc_type, exc_val, exc_tb)  
---
Closes the database connection when exiting a `with` block. This method is called automatically, even if an error occurred.  
  
#### __init__(self, db_user: str, db_password: str, db_host: str, db_driver: str)  
---
Initializes the class attributes for a database connection. The actual connection is established in the `__enter__` method.  
  
* **Args**:  
  
  * **`db_user` (`str`):** The user ID for the database connection.  
  * **`db_password` (`str`):** The password for the database user.  
  * **`db_host` (`str`):** The system/host name for the database connection.  
  * **`db_driver` (`str`):** The ODBC driver to be used.  
#### getInfoForLibrary()
---
Retrieves information about a specific library.  
  
**Args:**  
  
  * **`library` (`str`):** The name of the library to retrieve information about.  
  * **`wantJson` (`bool`, optional):** If set to `True`, the function returns a JSON-formatted string. If `False`, it returns a Python object. Defaults to `True`.  
**Returns:**  
  
  * **`str`:** A JSON string if `wantJson` is True.  
  * **`obj`:** A Python object if `wantJson` is False.  
  
**Example:**  
  
```python
from os.path import join, dirname  
import os  
from dotenv import load_dotenv  
import iLibrary  
  
#load ENV file and get the Connection Settings  
dotenv_path = join(dirname(__file__), '.env')  
load_dotenv(dotenv_path)  
DB_DRIVER = os.environ.get("DB_DRIVER")  
DB_USER = os.environ.get("DB_USER")  
DB_PASSWORD = os.environ.get("DB_PASSWORD")  
DB_SYSTEM = os.environ.get("DB_SYSTEM")  
  
  
if __name__ == "__main__":  
    try:  
        with iLibrary.Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:  
            #try to get the SAVF File from the IBM i Server  
            result = lib.getInfoForLibrary('LIB_NAME')  
            print(f"Query result: {result}")  
  
    except Exception as e:  
        print(f"An error occurred in the main block: {e}")
```
  
#### iclose(self)  
  ---
A helper method to close the connection, also useful for manual closure.  
  
#### saveLibrary()
---
  
Saves a complete library from the IBM i to a save file.  
  
This method creates a save file on the IBM i and then uses the `SAVLIB` (Save Library) CL command to save the specified library's contents into it. Optionally, it can download the resulting save file to the local machine as a ZIP file.  
  
**Args:**  
  
* **`library` (`str`):** The name of the library to be saved.  
  
* **`saveFileName` (`str`):** The name of the save file that will be created to hold the library.  
  
* **`description` (`str`, optional):** A text description for the save file. Defaults to None.  
  
* **`localPath` (`str`, optional):** The local file path where the downloaded save file will be stored. Required if `getZip` is True. Defaults to None.  
  
* **`remPath` (`str`, optional):** The remote file path on the IBM i's IFS where the save file will be temporarily stored before downloading. Required if `getZip` is True. Defaults to None.  
  
* **`getZip` (`bool`, optional):** If True, the save file will be downloaded to the local machine and then deleted from the remote IFS. Defaults to False.  
  
* **`port` (`int`, optional):** The port for the SSH connection. Defaults to 22.  
  
 **Returns:**
* **`bool`:** `True` if the library was saved successfully (and downloaded if requested), `False` otherwise.  
**Example**
```python
from os.path import join, dirname  
import os  
from dotenv import load_dotenv  
import iLibrary  
  
#load ENV file and get the Connection Settings  
dotenv_path = join(dirname(__file__), '.env')  
load_dotenv(dotenv_path)  
DB_DRIVER = os.environ.get("DB_DRIVER")  
DB_USER = os.environ.get("DB_USER")  
DB_PASSWORD = os.environ.get("DB_PASSWORD")  
DB_SYSTEM = os.environ.get("DB_SYSTEM")  
  
  
if __name__ == "__main__":  
    try:  
        with iLibrary.Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:  
            #try to get the SAVF File from the IBM i Server  
            result = lib.saveLibrary(library='YOUR_LIB',   saveFileName='SAVEFILE_NAME', getZip=True, localPath=join(dirname(__file__)), remPath='/home/USERNAME/')  
            print(f"Query result: {result}")  
  
    except Exception as e:  
        print(f"An error occurred in the main block: {e}")
```
  