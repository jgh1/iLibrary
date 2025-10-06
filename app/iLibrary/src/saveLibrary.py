from os.path import join
import paramiko
import pyodbc
import json
from datetime import datetime, date
from decimal import Decimal
class saveLibrary:
    # ------------------------------------------------------
    # saveLibrary - creating a Savefile and sending to the
    #               IFS
    # ------------------------------------------------------
    def saveLibrary(self,
                    library:str,
                    saveFileName:str,
                    toLibrary:str=None,
                    description:str=None,
                    localPath:str=None,
                    remPath:str=None,
                    getZip:bool=False,
                    port:int=None,
                    remSavf=True,
                    version:str=None
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
            Returns:
                bool: True if the library was saved successfully (and downloaded if requested),
                      False otherwise.
        """
        #check if something missing from the Arguments
        if not library:
            raise ValueError("A library name is required.")
        if not saveFileName:
            raise ValueError("A save file name is required.")
        if not toLibrary:
            toLibrary = library
        if getZip:
            if not remPath:
                raise ValueError("A remote path is required. Use 'remPath' instead.")
            elif remPath[-1] == '/':
                remPath = remPath[:-1]
            if not localPath:
                raise ValueError("A local path is required. Use 'localPath' instead.")
            elif localPath[-1] == '/':
                localPath = localPath[:-1]
        if not version:
            version = "*CURRENT"
        #starting with mem main Sourcecode of saveLLibrary
        if self.__crtsavf(saveFileName, toLibrary, description):

            command_str: str = f"SAVLIB LIB({library}) DEV(*SAVF) SAVF({toLibrary}/{saveFileName}) TGTRLS({version})"
            try:
                with self.conn.cursor() as cursor:
                    # execute the Command for creating a Savefile.
                    cursor.execute("CALL QSYS2.QCMDEXC(?)", (command_str))
                    if getZip:
                        try:
                            remote_temp_savf_path = join(remPath, saveFileName.upper() + '.savf')

                            destination_local_path = join(localPath, saveFileName.upper() + '.savf')
                            command_str = (
                                f"CPYTOSTMF FROMMBR('/QSYS.LIB/{toLibrary.upper()}.LIB/{saveFileName.upper()}.FILE') "
                                f"TOSTMF('{remote_temp_savf_path}') STMFOPT(*REPLACE)"
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
    def __crtsavf(self,
                  saveFileName:str,
                  library:str,
                  description:str=None
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
            print(f"An error occurred while executing command, with deleting SavFile: {e}")
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return True
