# Installation

This project targets Python 3.8+.

Prerequisites
- An IBM i (AS/400) system you can access.
- ODBC driver for IBM i installed locally (IBM i Access ODBC Driver or compatible).
- Network access from your machine to the IBM i for ODBC (DB2) and optional SFTP/SSH.

Install the package
- From PyPI: pip install iLibrary
- From source (this repository):
  - Clone the repo
  - Optional: create and activate a virtual environment
  - pip install -r requirements.txt
  - pip install -e .

Environment/connection settings
- DB_DRIVER: ODBC driver name, e.g. {IBM i Access ODBC Driver}
- DB_USER: IBM i user profile
- DB_PASSWORD: Password
- DB_SYSTEM: Hostname or IP address

Example .env
DB_DRIVER={IBM i Access ODBC Driver}
DB_USER=MYUSER
DB_PASSWORD=SECRET
DB_SYSTEM=myibmi.company.local

Verify ODBC connection
- Use isql, iSeries Access tools, or a simple pyodbc.connect test with your connection string to confirm connectivity before using the library.
