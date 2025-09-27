from os.path import join
import paramiko
import pyodbc
import json


class Library:
    """
    A class to manage libraries and files on an IBM i system.

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
    def __enter__(self) -> 'Library':
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
            return self
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
    # getInfoForLibrary - get all Infos over SQL about
    #                     the Library
    # ------------------------------------------------------
    def getInfoForLibrary(self, library:str, wantJson=True) -> None:
        """
        Retrieves information about a specific library.

        Args:
            library (str): The name of the library to retrieve information about.
            wantJson (bool, optional): If set to `True`, the function returns a JSON-formatted string.
                                       If `False`, it returns a Python object. Defaults to `True`.

        Returns:
            str: A JSON string if `wantJson` is True.
            obj: A Python object if `wantJson` is False.
        """


        if not library:
            raise ValueError("A library name is required.")
        if len(library) > 10:
            raise ValueError("The library name is too long. Maximum length is 10.")

        #Select the information about the Library
        sql_query = f"SELECT * FROM TABLE(QSYS2.LIBRARY_INFO(upper('{library}')))"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()
                # Check if any row was returned
                if not rows:
                    if wantJson:
                        rowsTitle = ['error']
                        errorString = f'No data found for library for Library: {library}'
                        row_to_dict = dict(zip(rowsTitle, [errorString]))
                        getJSON_String = json.dumps(row_to_dict, indent=4)
                        return getJSON_String
                    tmpReturnTuple:tuple = ('error', 'No data found for library')
                    return tmpReturnTuple

                # Get the single tuple from the list of rows
                row_tuple = rows[0]
                if wantJson:
                    rowsTitle = [
                        'OBJECT_COUNT',
                        'LIBRARY_SIZE',
                        'LIBRARY_SIZE_COMPLETE',
                        'LIBRARY_TYPE',
                        'TEXT_DESCRIPTION',
                        'IASP_NAME',
                        'IASP_NUMBER',
                        'CREATE_AUTHORITY',
                        'OBJECT_AUDIT_CREATE',
                        'JOURNALED',
                        'JOURNAL_LIBRARY',
                        'JOURNAL_NAME',
                        'INHERIT_JOURNALING',
                        'JOURNAL_INHERIT_RULES',
                        'JOURNAL_START_TIMESTAMP',
                        'APPLY_STARTING_RECEIVER_LIBRARY',
                        'APPLY_STARTING_RECEIVER',
                        'APPLY_STARTING_RECEIVER_ASP'
                    ]

                    # Zip the list of titles with the single row tuple
                    row_to_dict = dict(zip(rowsTitle, row_tuple))

                    getJSON_String = json.dumps(row_to_dict, indent=4)
                    return getJSON_String

                #if wantJSON false, return back a tuple
                return row_tuple

        except Exception as e:
            print(f"An error occurred while fetching data: {e}")
            return None

    # ------------------------------------------------------
    # saveLibrary - creating a Savefile and sending to the
    #               IFS
    # ------------------------------------------------------
    def saveLibrary(self, library:str, saveFileName:str, description:str=None, localPath:str=None, remPath:str=None, getZip:bool=False, port:int=None ) -> bool:
        """
            Saves a complete library from the IBM i to a save file.

            This method creates a save file on the IBM i and then uses the `SAVLIB`
            (Save Library) CL command to save the specified library's contents into it.
            Optionally, it can download the resulting save file to the local machine
            as a ZIP file.

            Args:
                library (str): The name of the library to be saved.
                saveFileName (str): The name of the save file that will be created to hold the library.
                description (str, optional): A text description for the save file. Defaults to None.
                localPath (str, optional): The local file path where the downloaded save file will be stored.
                                           Required if `getZip` is True. Defaults to None.
                remPath (str, optional): The remote file path on the IBM i's IFS where the
                                         save file will be temporarily stored before downloading.
                                         Required if `getZip` is True. Defaults to None.
                getZip (bool, optional): If True, the save file will be downloaded to the local machine
                                         and then deleted from the remote IFS. Defaults to False.
                port (int, optional): The port for the SSH connection. Defaults to 22.

            Returns:
                bool: True if the library was saved successfully (and downloaded if requested),
                      False otherwise.
        """
        #check if something missing from the Arguments
        if not library:
            raise ValueError("A library name is required.")
        if not saveFileName:
            raise ValueError("A save file name is required.")
        if getZip:
            if not remPath:
                raise ValueError("A remote path is required. Use 'remPath' instead.")
            elif remPath[-1] == '/':
                remPath = remPath[:-1]
            if not localPath:
                raise ValueError("A local path is required. Use 'localPath' instead.")
            elif localPath[-1] == '/':
                localPath = localPath[:-1]

        #starting with mem main Sourcecode of saveLLibrary
        if self.__crtsavf(saveFileName, library, description):

            command_str: str = f"SAVLIB LIB({library}) DEV(*SAVF) SAVF({library}/{saveFileName})"
            try:
                with self.conn.cursor() as cursor:
                    # execute the Command for creating a Savefile.
                    cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str))
                    if getZip:
                        try:
                            remote_temp_savf_path = join(remPath, saveFileName.upper() + '.savf')

                            destination_local_path = join(localPath, saveFileName.upper() + '.savf')
                            command_str = (
                                f"CPYTOSTMF FROMMBR('/QSYS.LIB/{library.upper()}.LIB/{saveFileName.upper()}.FILE') "
                                f"TOSTMF('{remote_temp_savf_path}') STMFOPT(*REPLACE)"
                            )

                            # Execute the command on the remote system
                            cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str,))

                            if  self.__getZipFile(localFilePath=destination_local_path,
                                                     remotePath=remote_temp_savf_path, port=port):
                                rmvCommand = f"QSH CMD('rm -r {remote_temp_savf_path}')"
                                cursor.execute("CALL QSYS2.QCMDEXC(?)", (rmvCommand))
                            else:
                                raise ValueError("Something went wrong. With downloading the Save File.")

                        except Exception as e:

                            print(f"An error occurred during the transfer process: {e}")

            except Exception as e:
                print(f"An error occurred while executing command: {e}")
                self.conn.rollback()
                return False
            else:
                self.conn.commit()
                if getZip:
                    print(f"File successfully downloaded to: {destination_local_path}")
                    return True

                print(f"Successfully saved in the Library '{library}' successfully.")
                return True

        return False

    # ------------------------------------------------------
    # sub Function: create the Savefile on the AS400
    # ------------------------------------------------------
    def __crtsavf(self, saveFileName:str, library:str, description:str=None) -> bool:
        """
            Sub-function to create a save file on the IBM i server.

            This function executes the `CRTSAVF` (Create Save File) CL command
            to create a new save file in the specified library. This is a
            prerequisite for saving a library's contents.

            Args:
                saveFileName (str): The name of the save file to be created.
                                    This will be the AS/400 object name.
                library (str): The name of the library where the save file will be created.
                description (str, optional): A text description for the save file. Defaults to None.

            Returns:
                bool: True if the save file was created successfully, False otherwise.
        """
        # check is a parameter empty or not

        if not saveFileName:
            raise ValueError("A file name is required.")
        if not library:
            raise ValueError("A library name is required.")
        if not description:
            description = 'A SaveFile from iLibrary'

        # prepare the Command String for creating a Savefile on the AS400 Server.

        command_str:str = f"CRTSAVF FILE({library.upper()}/{saveFileName.upper()}) TEXT('{description}')"

        try:
            with self.conn.cursor() as cursor:
                #execute the Command for creating a Savefile.
                cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str))

        except Exception as e:
            print(f"An error occurred while executing command: {e}")
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True

    # ------------------------------------------------------
    # getZipFile - getting the Zipfile from the SaveFile
    # ------------------------------------------------------
    def __getZipFile(self, localFilePath: str, remotePath: str, port:int=None) -> bool:
        """
            Downloads a file from the remote IBM i via SFTP.

            This method uses Paramiko to establish a secure shell (SSH) connection and
            then an SFTP session to transfer a file from a specified remote location
            on the IBM i's IFS to a local path.

            Args:
                remote_file_path (str): The full path to the file on the remote IBM i's IFS.
                local_save_path (str): The full path on the local machine where the file
                                       will be saved. For example, '/Users/user/Documents/somefile.savf'.

            Returns:
                bool: True if the file was downloaded successfully, False otherwise.

            Raises:
                ValueError: If either the remote_file_path or local_save_path is not provided.
        """
        if not localFilePath:
            print("Error: A local file path is required.")
            return False
        if not remotePath:
            print("Error: A remote path is required.")
            return False
        if not port:
            port = 2222
        ssh_client = paramiko.SSHClient()

        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            with ssh_client:
                ssh_client.connect(
                    hostname=self.db_host,
                    username=self.db_user,
                    password=self.db_password,
                    port=port
                )
                with ssh_client.open_sftp() as ftp_client:
                    ftp_client.get(remotePath, localFilePath)
                    return True

        except paramiko.ssh_exception.AuthenticationException as e:
            print(f"Authentication failed. Check your username and password: {e}")
            return False
        except paramiko.ssh_exception.SSHException as e:
            print(f"SSH error occurred: {e}")
            return False
        except FileNotFoundError as e:
            print(f"File not found on the remote host: {e}")
            return False

        finally:
            pass

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