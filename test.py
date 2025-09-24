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
