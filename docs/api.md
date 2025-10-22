### `Library` Class API Reference

A context-managed client for interacting with IBM i libraries. It combines database operations via `pyodbc` with remote file system and command execution via `paramiko`.

---

### Constructor

The constructor initializes the object with connection details. The database connection itself is deferred until the context is entered.

`Library(db_user: str, db_password: str, db_host: str, db_driver: str)`

-   **`db_user`**: IBM i user profile.
-   **`db_password`**: User profile password.
-   **`db_host`**: Hostname or IP address of the IBM i system.
-   **`db_driver`**: The exact name of the ODBC driver, e.g., `{IBM i Access ODBC Driver}`. This must be installed on the client machine.

---

### Context Management

The class is designed to be used as a context manager with a `with` statement. This pattern ensures that the database connection is automatically opened and closed.

-   **`__enter__()`**: Opens the `pyodbc` connection. Returns the `Library` instance. Raises `pyodbc.Error` on failure.
-   **`__exit__()`**: Closes the database connection, even if exceptions occur within the `with` block.
-   **`iclose()`**: A manual method to close the connection. This is only necessary if not using a `with` statement.

---

### Methods

#### **Inspection**

-   **`getLibraryInfo(library: str, wantJson: bool = True) -> str | tuple`**
    Queries `QSYS2.LIBRARY_INFO` for library metadata.
    -   Raises `ValueError` if the library name exceeds 10 characters.

-   **`getFileInfo(library: str, qFiles: bool = False) -> str`**
    Lists objects within a specified library.
    -   If `qFiles` is `True`, the list is filtered to include only source physical files (`*FILE` with `PF-SRC` attribute).

#### **Backup and Cleanup**

-   **`saveLibrary(...) -> bool`**
    Executes a multi-step process to back up a library into a save file (SAVF) and optionally download it.
    1.  Creates a SAVF object on the IBM i.
    2.  Runs the `SAVLIB` command to save the specified library to that SAVF.
    3.  If `getZip=True`, it connects via SFTP and downloads the SAVF to a local path.

    **Primary Parameters:**
    -   **`library`**: The name of the library to save.
    -   **`saveFileName`**: The name of the SAVF to create (e.g., `MYLIBSAVF`).
    -   **`getZip`**: Set to `True` to download the file.
    -   **`localPath`**: The local file path to save the downloaded SAVF. Required if `getZip=True`.
    -   **`remPath`**: The remote path for the SAVF, if not in the default library.

    **Advanced IBM i Parameters:**
    -   These parameters map directly to `SAVLIB` command options for specialized use cases: `dev`, `vol`, `toLibrary`, `description`, `version`, `max_records`, `asp`, `waitFile`, `share`, `authority`.

-   **`removeFile(library: str, saveFileName: str) -> bool`**
    Deletes a specified SAVF from a library on the IBM i.

---

### Exceptions

-   **`pyodbc.Error`**: Raised during `__enter__` if the database connection fails.
-   **`ValueError`**: Raised by methods if input parameters are invalid (e.g., library name format).
-   **`paramiko.SSHException`, `socket.error`**: Raised during SFTP operations within `saveLibrary` if the remote connection fails.

---

### Example Usage

```python
from os.path import join, dirname
import os
import iLibrary

DB_CREDENTIALS = {
    "db_user": 'DB_USER',
    "db_password": 'DB_PASSWORD',
    "db_host": 'DB_HOST',
    "db_driver": '{IBM i Access ODBC Driver}'
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
```