# Usage

Quick start
- Install and configure per docs/installation.md
- Create a .env with DB settings or supply directly
- Use the Library class as a context manager to ensure connections are opened/closed

Example: get library information
```python
from os.path import join, dirname
import os
from dotenv import load_dotenv
from iLibrary import Library

# Load env variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")

with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
    info_json = lib.getLibraryInfo('QGPL', wantJson=True)
    print(info_json)
```

List files and objects in a library
```python
with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
    files_json = lib.getFileInfo('MYLIB')  # set qFiles=True for source physical files
    print(files_json)
```

Save a library to a save file (SAVF) and optionally download it
```python
from os.path import dirname

with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
    ok = lib.saveLibrary(
        library='MYLIB',
        saveFileName='MYLIBSAVE',
        description='Backup MYLIB',
        localPath=dirname(__file__),   # where to store the downloaded file
        remPath='/home/MYUSER/',       # remote path on IBM i IFS for temporary SAVF
        getZip=True                    # download and clean up on server
    )
    print('Saved:', ok)
```

Remove a save file on IBM i
```python
with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
    ok = lib.removeFile(library='MYLIB', saveFileName='MYLIBSAVE')
    print('Removed:', ok)
```

Notes
- The same IBM i credentials are used for ODBC and SSH/SFTP operations.
- Ensure your user profile has the required authorities to run SAVLIB and access IFS paths.
- Library names on IBM i are max 10 characters.
