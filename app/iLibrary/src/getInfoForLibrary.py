from os.path import join
import paramiko
import pyodbc
import json
from datetime import datetime, date
from decimal import Decimal
class getInfoForLibrary:
    """
    A class to show libraries and files on an IBM i system.
    """
    # ------------------------------------------------------
    # getInfoForLibrary - get all Infos over SQL about
    #                     the Library
    # ------------------------------------------------------
    def getLibraryInfo(self, library: str, wantJson=True) -> str:
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

        # Select the information about the Library
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
                    tmpReturnTuple: tuple = ('error', 'No data found for library')
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

                # if wantJSON false, return back a tuple
                return row_tuple

        except Exception as e:
            print(f"An error occurred while fetching data: {e}")
            return None

    # ------------------------------------------------------
    # getFileInfo - get all Files and Infos from a Lib
    # ------------------------------------------------------
    def getFileInfo(self, library:str, qFiles:bool=False) -> str:
        """
        getFileInfo - get all Files and Infos from a Lib
        :param library: The name of the library where the save file will be created.
        :param qFiles: If true, get all Files and Infos from Source Physical File
        :return:
            str: A Json String with all Files and Infos from a Library
        """
        if not library:
            raise ValueError("A library name is required.")


        try:
            with self.conn.cursor() as cursor:
                # execute the Command for deleting a Savefile.
                if not qFiles:
                    row_title = [
                        'OBJNAME',
                        'OBJTYPE',
                        'OBJOWNER',
                        'OBJDEFINER',
                        'OBJCREATED',
                        'OBJSIZE',
                        'OBJTEXT',
                        'OBJLONGNAME',
                        'LAST_USED_TIMESTAMP',
                        'LAST_USED_OBJECT',
                        'DAYS_USED_COUNT',
                        'LAST_RESET_TIMESTAMP',
                        'IASP_NUMBER',
                        'IASP_NAME',
                        'OBJATTRIBUTE',
                        'OBJLONGSCHEMA',
                        'TEXT',
                        'SQL_OBJECT_TYPE',
                        'OBJLIB',
                        'CHANGE_TIMESTAMP',
                        'USER_CHANGED',
                        'SOURCE_FILE',
                        'SOURCE_LIBRARY',
                        'SOURCE_MEMBER',
                        'SOURCE_TIMESTAMP',
                        'CREATED_SYSTEM',
                        'CREATED_SYSTEM_VERSION',
                        'LICENSED_PROGRAM',
                        'LICENSED_PROGRAM_VERSION',
                        'COMPILER',
                        'COMPILER_VERSION',
                        'OBJECT_CONTROL_LEVEL',
                        'BUILD_ID',
                        'PTF_NUMBER',
                        'APAR_ID',
                        'USER_DEFINED_ATTRIBUTE',
                        'ALLOW_CHANGE_BY_PROGRAM',
                        'CHANGED_BY_PROGRAM',
                        'COMPRESSED',
                        'PRIMARY_GROUP',
                        'STORAGE_FREED',
                        'ASSOCIATED_SPACE_SIZE',
                        'OPTIMUM_SPACE_ALIGNMENT',
                        'OVERFLOW_STORAGE',
                        'OBJECT_DOMAIN',
                        'OBJECT_AUDIT',
                        'OBJECT_SIGNED',
                        'SYSTEM_TRUSTED_SOURCE',
                        'MULTIPLE_SIGNATURES',
                        'SAVE_TIMESTAMP',
                        'RESTORE_TIMESTAMP',
                        'SAVE_WHILE_ACTIVE_TIMESTAMP',
                        'SAVE_COMMAND',
                        'SAVE_DEVICE',
                        'SAVE_FILE_NAME',
                        'SAVE_FILE_LIBRARY',
                        'SAVE_VOLUME',
                        'SAVE_LABEL',
                        'SAVE_SEQUENCE_NUMBER',
                        'LAST_SAVE_SIZE',
                        'JOURNALED',
                        'JOURNAL_NAME',
                        'JOURNAL_LIBRARY',
                        'JOURNAL_IMAGES',
                        'OMIT_JOURNAL_ENTRY',
                        'REMOTE_JOURNAL_FILTER',
                        'JOURNAL_START_TIMESTAMP',
                        'APPLY_STARTING_RECEIVER',
                        'APPLY_STARTING_RECEIVER_LIBRARY',
                        'AUTHORITY_COLLECTION_VALUE'
                    ]
                    #generate Normal CMD Command
                    cmdString = f"SELECT * FROM TABLE (QSYS2.OBJECT_STATISTICS('{library}','*ALL') ) AS X"

                if qFiles:
                    cmdString = f"SELECT * FROM QSYS2.SYSMEMBERSTAT WHERE SYSTEM_TABLE_SCHEMA = '{library}' AND SOURCE_TYPE IS NOT NULL ORDER BY SYSTEM_TABLE_MEMBER"
                    row_title = [
                        'TABLE_SCHEMA',
                        'TABLE_NAME',
                        'SYSTEM_TABLE_SCHEMA',
                        'SYSTEM_TABLE_NAME',
                        'SYSTEM_TABLE_MEMBER',
                        'SOURCE_TYPE',
                        'LAST_SOURCE_UPDATE_TIMESTAMP',
                        'TEXT_DESCRIPTION',
                        'CREATE_TIMESTAMP',
                        'LAST_CHANGE_TIMESTAMP',
                        'LAST_SAVE_TIMESTAMP',
                        'LAST_RESTORE_TIMESTAMP',
                        'LAST_USED_TIMESTAMP',
                        'DAYS_USED_COUNT',
                        'LAST_RESET_TIMESTAMP',
                        'TABLE_PARTITION',
                        'PARTITION_TYPE',
                        'PARTITION_NUMBER',
                        'NUMBER_DISTRIBUTED_PARTITIONS',
                        'NUMBER_PARTITIONING_KEYS',
                        'PARTITIONING_KEYS',
                        'LOWINCLUSIVE',
                        'LOWVALUE',
                        'HIGHINCLUSIVE',
                        'HIGHVALUE',
                        'NUMBER_ROWS',
                        'NUMBER_PAGES',
                        'OVERFLOW',
                        'AVGROWSIZE',
                        'NUMBER_DELETED_ROWS',
                        'DATA_SIZE',
                        'VARIABLE_LENGTH_SIZE',
                        'VARIABLE_LENGTH_SEGMENTS',
                        'COLUMN_STATS_SIZE',
                        'MAINTAINED_TEMPORARY_INDEX_SIZE',
                        'NUMBER_DISTINCT_INDEXES',
                        'OPEN_OPERATIONS',
                        'CLOSE_OPERATIONS',
                        'INSERT_OPERATIONS',
                        'BLOCKED_INSERT_OPERATIONS',
                        'BLOCKED_INSERT_ROWS',
                        'UPDATE_OPERATIONS',
                        'DELETE_OPERATIONS',
                        'CLEAR_OPERATIONS',
                        'COPY_OPERATIONS',
                        'REORGANIZE_OPERATIONS',
                        'INDEX_BUILDS',
                        'LOGICAL_READS',
                        'PHYSICAL_READS',
                        'SEQUENTIAL_READS'
                        'RANDOM_READS',
                        'NEXT_IDENTITY_VALUE',
                        'KEEP_IN_MEMORY',
                        'MEDIA_PREFERENCE',
                        'VOLATILE',
                        'PARTIAL_TRANSACTION',
                        'APPLY_STARTING_RECEIVER_LIBRARY',
                        'APPLY_STARTING_RECEIVER'
                    ]

                cursor.execute(cmdString)


                result_list = []
                rows = cursor.fetchall()
                if len(rows) == 0:
                    return f'No Files Found in Library: {library}'
                for row in rows:
                    # 1. Create the dictionary for the current row
                    row_dict = dict(zip(row_title, row))

                    # 2. Iterate through the dictionary's items to find and convert datetimes
                    for key, value in row_dict.items():
                        if isinstance(value, (datetime, date)):
                            # Convert the datetime object to a standardized ISO 8601 string
                            row_dict[key] = value.isoformat()
                        elif isinstance(value, Decimal):
                            row_dict[key] = str(value)

                    # 3. Append the now JSON-safe dictionary to the list
                    result_list.append(row_dict)

                # Convert the list of dictionaries into a JSON string
                json_string = json.dumps(result_list, indent=4)
        except Exception as e:
            print(f"An error occurred while executing command, with showing Lib Files: {e}")
            self.conn.rollback()
            return False
        else:
            self.conn.commit()
            return json_string
