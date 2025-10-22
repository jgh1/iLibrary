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
DB_CREDENTIALS = {
    "db_user": DB_USER,
    "db_password": DB_PASSWORD,
    "db_host": DB_SYSTEM,
    "db_driver": DB_DRIVER
}


if __name__ == "__main__":
    try:
        with iLibrary.Library(**DB_CREDENTIALS) as lib:
            # Backup a library and download the save file
            was_saved = lib.saveLibrary(
                library='YOURPRODLIB',
                saveFileName='PRODLIBSAV',
                getZip=True,
                localPath=f'{os.getcwd()}/backups',
                remPath='/home/<YOUR USERNAME>/',
                remSavf=True
            )

            if was_saved:
                print("Backup successful. Cleaning up remote file.")
                lib.removeFile(library='PRODLIB', saveFileName='PRODLIBSAV')

    except ValueError as e:
        print(f"Invalid parameter specified: {e}")