# iLibrary

A lightweight Python helper for working with IBM i (AS/400) libraries. It connects via ODBC (pyodbc) for DB2/SQL queries and uses Paramiko for SSH/SFTP to save and transfer library save files (SAVF).

[PyPI downloads](https://pepy.tech/projects/ilibrary)

Overview
- Query library metadata using QSYS2 services
- List objects in a library (and optionally source physical files)
- Create a save file (SAVF) for a library via SAVLIB and optionally download it
- Remove save files
- Simple context manager to handle DB connection lifecycle

Requirements
- Python 3.8+
- IBM i system access
- IBM i Access ODBC Driver (or compatible) installed locally
- Network access to the IBM i for ODBC and SSH/SFTP

Installation
- From PyPI: pip install iLibrary
- From source:
  - Clone the repo
  - Optionally create and activate a virtual environment
  - pip install -r requirements.txt
  - pip install -e .

Quickstart
```python
from os.path import join, dirname
import os
from dotenv import load_dotenv
from iLibrary import Library

# Load ENV file and get the connection settings
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")

with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
    print(lib.getLibraryInfo('QGPL', wantJson=True))
    print(lib.getFileInfo('QGPL'))
```

Save a library to SAVF and optionally download it
```python
from os.path import dirname

with Library(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
    ok = lib.saveLibrary(
        library='MYLIB',
        saveFileName='MYLIBSAVE',
        description='Backup',
        localPath=dirname(__file__),
        remPath='/home/MYUSER/',
        getZip=True
    )
    print('Saved:', ok)
```

API overview
- Library(db_user, db_password, db_host, db_driver)
  - __enter__ / __exit__ for connection lifecycle
  - iclose(): manually close the connection
- getLibraryInfo(library: str, wantJson: bool = True) -> str | tuple
- getFileInfo(library: str, qFiles: bool = False) -> str
- saveLibrary(library: str, saveFileName: str, ..., getZip: bool = False, ...) -> bool
- removeFile(library: str, saveFileName: str) -> bool

Configuration
- Environment variables expected:
  - DB_DRIVER: e.g. {IBM i Access ODBC Driver}
  - DB_USER
  - DB_PASSWORD
  - DB_SYSTEM

Documentation
- Installation guide: [[docs/installation.md]]
- Usage examples: [[docs/usage.md]]
- Full API reference: [[docs/api.md]]
- Troubleshooting: [[docs/troubleshooting.md]]

Contributing
- Please run tests or the sample script before submitting changes.

License
- See the repository license file if present.
  