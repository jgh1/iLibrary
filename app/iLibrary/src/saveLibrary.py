from _ast import Raise
from os.path import join
import paramiko
import pyodbc
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Union

class saveLibrary:
    # ------------------------------------------------------
    # saveLibrary - creating a Savefile and sending to the
    #               IFS
    # ------------------------------------------------------
    def saveLibrary(self,
                    library:str,
                    saveFileName:str,
                    dev: str = None,
                    vol:str=None,
                    toLibrary:str=None,
                    description:str=None,
                    localPath:str=None,
                    remPath:str=None,
                    getZip:bool=False,
                    port:int=None,
                    remSavf=True,
                    version:str=None,
                    max_records: Union[int, str, None] = None,
                    asp: Union[int, str, None] = None,
                    waitFile: Union[int, str, None] = None,
                    share: str = None,
                    authority: str = None
                ) -> bool:
        """
            Saves a complete library from the IBM i to a save file.

            This method creates a save file on the IBM i and then uses the `SAVLIB`
            (Save Library) CL command to save the specified library's contents into it.
            Optionally, it can download the resulting save file to the local machine
            as a ZIP file.

            Args:
                library (str): The name of the library to be saved.
                saveFileName (str): The name of the save file that will be created to hold the library.
                dev (str, optional): The device type for the save file. Defaults to '*SAVF'.
                vol (str, optional): The volume to be used for saving the Library. Defaults is None.
                toLibrary (str, optional): The name of the library to be saved.
                description (str, optional): A text description for the save file. Defaults to None.
                localPath (str, optional): The local file path where the downloaded save file will be stored.
                                           Required if `getZip` is True. Defaults to None.
                remPath (str, optional): The remote file path on the IBM i's IFS where the
                                         save file will be temporarily stored before downloading.
                                         Required if `getZip` is True. Defaults to None.
                getZip (bool, optional): If True, the save file will be downloaded to the local machine
                                         and then deleted from the remote IFS. Defaults to False.
                port (int, optional): The port for the SSH connection. Defaults to 22.
                remSavf (bool, optional): If True, the save file will be automatacly removed from the remote after downloading.
                version (str): The version of the save file. Defaults to *CURRENT.
                max_records (int, str, optional): The maximum number of records to return. Defaults to *NOMAX. (*NOMAX, 1 - 4293525600)
            Returns:
                bool: True if the library was saved successfully (and downloaded if requested),
                      False otherwise.
        """
        # Target Release List
        trgList:list = ["V1R1M0", "V1R1M2", "V1R2M0", "V1R3M0", "V2R1M0", "V2R1M1",
                        "V2R2M0", "V2R3M0", "V3R0M5", "V3R1M0", "V3R2M0", "V3R6M0",
                        "V3R7M0", "V4R1M0", "V4R2M0", "V4R3M0", "V4R4M0", "V4R5M0",
                        "V5R1M0", "V5R2M0", "V5R3M0", "V5R4M0", "V6R1M0", "V6R1M1",
                        "V7R1M0", "V7R2M0", "V7R3M0", "V7R4M0", "V7R5M0", "V7R6M0"]

        # check if something missing from the Arguments
        #check if Library is empty or not
        if not library:
            raise ValueError("A library name is required.")
        # check if saveFileName is empty or not
        if not saveFileName:
            raise ValueError("A save file name is required.")
        #check if toLibrary is empty or not
        if not toLibrary:
            toLibrary = library
        #check if user want the SaveFile as ZIP File
        if getZip:
            if not remPath:
                raise ValueError("A remote path is required. Use 'remPath' instead.")
            elif remPath[-1] == '/':
                remPath = remPath[:-1]
            if not localPath:
                raise ValueError("A local path is required. Use 'localPath' instead.")
            elif localPath[-1] == '/':
                localPath = localPath[:-1]
        #check wich Version of SaveFile is wanted
        if not version in list(trgList):
            version = "*CURRENT"
        else:
            version = version.upper()
        command_str:str = f'SAVLIB'

        #check if Library is valid or not
        validated_library =  self.__validate_max_value(value=library, param_name='library', str_format=['*NONSYS', '*ALLUSR', '*IBM', '*SELECT', '*USRSPC', library])
        if validated_library:
            command_str += f' LIB({validated_library})'
        else:
            library_str = str(library)
            raise ValueError(f"The library '{library_str}' is not valid. Must be one of the specified strings or a valid number.")
        #check Dev - Device
        if not dev in ['*SAVF', '*MEDDFN']:
            command_str += f' DEV(*SAVF)'
        else:
            command_str += f' DEV({dev.upper()})'
        if vol is not None and vol == '*MOUNTED':
            command_str += f' VOL({vol})'
        #starting with mem main Sourcecode of saveLLibrary
        if self.__crtsavf(saveFileName, toLibrary, description, max_records=max_records, asp=asp, waitFile=waitFile, share=share, authority=authority):
            #command_str: str = f"SAVLIB LIB({library.strip()}) DEV(*SAVF) SAVF({toLibrary.strip()}/{saveFileName.strip()}) TGTRLS({version.strip()})"
            command_str += f" SAVF({toLibrary.strip()}/{saveFileName.strip()}) TGTRLS({version.strip()})"
            print(command_str)
            try:
                with self.conn.cursor() as cursor:
                    # execute the Command for creating a Savefile.
                    cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str))
                    if getZip:
                        try:
                            remote_temp_savf_path = join(remPath, saveFileName.upper() + '.savf')

                            destination_local_path = join(localPath, saveFileName.upper() + '.savf')
                            command_str = (
                                f"CPYTOSTMF FROMMBR('/QSYS.LIB/{toLibrary.upper().strip()}.LIB/{saveFileName.upper().strip()}.FILE') "
                                f"TOSTMF('{remote_temp_savf_path.strip()}') STMFOPT(*REPLACE)"
                            )

                            # Execute the command on the remote system
                            cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str,))

                            if  self.__getSavFile(localFilePath=destination_local_path,
                                                     remotePath=remote_temp_savf_path, port=port):
                                rmvCommand = f"QSH CMD('rm -r {remote_temp_savf_path}')"
                                cursor.execute("CALL QSYS2.QCMDEXC(?)", (rmvCommand))
                            else:
                                raise ValueError("Something went wrong. With downloading the Save File.")
                            if remSavf:
                                if not self.removeFile(library=toLibrary, saveFileName=saveFileName):
                                    raise ValueError(f"The Save File {saveFileName} was not successfully removed.")

                        except Exception as e:
                            self.__handle_error(error=e, pgm="saveLibrary - Transfer")

            except Exception as e:
                self.__handle_error(error=e, pgm="saveLibrary")
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
    def __crtsavf(self,
                  saveFileName:str,
                  library:str,
                  description:str=None,
                  max_records: Union[int, str, None] = None,
                  asp: Union[int, str, None] = None,
                  waitFile: Union[int, str, None] = None,
                  share:str=None,
                  authority:str=None
                ) -> bool:
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

        command_str: str = f"CRTSAVF FILE({library.upper().strip()}/{saveFileName.upper().strip()}) TEXT('{description.strip()}')"

        #check max_records for MAXRCDS parameter
        if self.__validate_max_value(value=max_records, param_name='max_records', str_format=['*NOMAX'], max_limit=4293525600) and not None:
            command_str += f" MAXRCDS({max_records})"
        #check asp for ASP 2147483647
        if self.__validate_max_value(value=asp, param_name='asp', str_format=['*LIBASP'], max_limit=32) and not None:
            command_str += f" ASP({asp})"
        if self.__validate_max_value(value=waitFile,param_name='waitFile', str_format=['*IMMED', '*CLS'], max_limit=2147483647) and not None:
            command_str += f" WAITFILE({waitFile})"
        if self.__validate_max_value(value=share, param_name='share', str_format=['*YES', '*NO']) and not None:
            command_str += f" SHARE({share})"

        if authority is not None:
            upper_authority = authority.upper()

            # 1. Check for custom authority (not in list AND up to 10 chars)
            if upper_authority not in ['*EXCLUDE', '*ALL', '*CHANGE', '*LIBCRTAUT', '*USE'] and len(
                    upper_authority) <= 10:
                # **CORRECTION 1: Use upper_authority here, not the undefined 'auth'**
                command_str += f" AUT({upper_authority})"
                # The 'pass' statements are redundant and can be removed

            # 2. Add an 'elif' to handle the case where it IS one of the standard values
            elif upper_authority in ['*EXCLUDE', '*ALL', '*CHANGE', '*LIBCRTAUT', '*USE']:
                command_str += f" AUT({upper_authority})"

        print (command_str)
        try:
            with self.conn.cursor() as cursor:
                #execute the Command for creating a Savefile.
                cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str))

        except Exception as e:
            self.__handle_error(error=e, pgm="__crtsavf")
            #remove a SAVF if its exists and we got an error
            if e.args[0] == 'HY000':
                sql = """
                      SELECT 1
                      FROM QSYS2.SAVE_FILE_INFO
                      WHERE SAVE_FILE_LIBRARY = ? \
                        AND SAVE_FILE = ?
                          FETCH FIRST 1 ROW ONLY \
                      """
                cursor = self.conn.cursor()
                cursor.execute(sql, library, saveFileName)
                result = cursor.fetchone()
                if result is not None:
                    self.removeFile(library=library, saveFileName=saveFileName)
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True

    # --------------------------------------------------------------------------
    # __validate_max_value - Helper Function for checking parameter
    # --------------------------------------------------------------------------
    def __validate_max_value(self,
                             value: Union[int, str, None],
                             param_name: str,
                             str_format: list[str],
                             min_limit: int = 1,
                             max_limit: int = None
                             ) -> Union[int, str, bool]:  # Includes bool as requested
        """
        Validates an input value for 'MAX' type parameters against a custom range.
        Handles special strings defined in str_format and numeric values.

        Returns: The validated integer, the standardized special string, or False on failure (if no exception is raised).
        Raises: ValueError for invalid string format or out-of-range number.
        """

        # Helper for clear error messages
        str_options = ", ".join([f"'{s}'" for s in str_format])

        # 1. Handle special string
        if isinstance(value, str):
            upper_value = value.upper()

            for special_value in str_format:
                normalized_special_value = special_value.upper()

                if upper_value == special_value.upper() or upper_value == normalized_special_value:
                    # Found a match! Return the official, fully formatted string.
                    return special_value

        # 2. Attempt Numeric Conversion (handles int and string-of-int)
        if value is not None:
            try:
                numeric_value = int(value)
            except ValueError:
                # Value is an invalid string (e.g., 'hello')
                raise ValueError(
                    f"Invalid value for {param_name}. Must be '{str_format}' or a number "
                    f"between {min_limit} and {max_limit:,}."
                )
        else:
            # If the value is None
            return False

        # 3. Check Numeric Range
        if min_limit <= numeric_value <= max_limit:
            return numeric_value
        else:
            # Number is out of range
            raise ValueError(
                f"Invalid numeric value for {param_name}. Must be between {min_limit} and {max_limit:,}. "
                f"Received: {numeric_value}"
            )
    # ------------------------------------------------------
    # getZipFile - getting the Zipfile from the SaveFile
    # ------------------------------------------------------
    def __getSavFile(self,
                     localFilePath: str,
                     remotePath: str,
                     port:int=None
                    ) -> bool:
        """
            Downloads a file from the remote IBM i via SFTP.

            This method uses Paramiko to establish a secure shell (SSH) connection and
            then an SFTP session to transfer a file from a specified remote location
            on the IBM i's IFS to a local path.

            Args:
                localFilePath (str): The full path to the file on the remote IBM i's IFS.
                remotePath (str): The full path on the local machine where the file
                                       will be saved. For example, '/Users/user/Documents/somefile.savf'.
                port (int, optional): The port to connect to the IBMi server. Defaults to None.

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

    def removeFile(self, library:str, saveFileName:str) -> bool:
        """
        Remove a (saved) file from the library on the AS400.
        :param library: The name of the library where the save file will be created.
        :param saveFileName: The name of the save file to be created.
        :return:
        Boolean: True if the file was removed successfully, False otherwise.
        """
        command_str: str = f"DLTF FILE({library.upper()}/{saveFileName.upper()})"
        try:
            with self.conn.cursor() as cursor:
                # execute the Command for deleting a Savefile.
                cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str))

        except Exception as e:
            self.__handle_error(error=e, pgm="removeFile")
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True


    def __handle_error(self, error, pgm:str):
        """
            Handle ODBC Errors and foramt them
        :param error:
        :param pgm:
        :return:
        """
        print("-------------------------------------------------------------")
        print(f"An error occurred while executing command in function {pgm}:")
        sqlstate = error.args[0]
        error_message = error.args[1]

        print(f"SQLSTATE: {sqlstate}")
        print(f"Message: {error_message}")