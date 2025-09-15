import pyodbc
import json

class Library:
    """
    A class to manage database connections and execute SQL commands on IBM i.
    """
    def __init__(self, conn):
        """
        Initializes the class with an active database connection.

        Args:
            conn: An active pyodbc or similar database connection object.
        """
        # The .connected attribute check is not valid for pyodbc.
        # A successful connect() call already ensures the connection is active.
        if not conn:
            raise ValueError("An active database connection is required.")
        self.conn = conn

    def getInfoForLibrary(self, library:str) -> dict:
        """
        Retrieves information about a specific library.
        """
        sql_query = f"SELECT * FROM TABLE(QSYS2.LIBRARY_INFO('{library}'))"
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(sql_query)
                rows = cursor.fetchall()

                # Check if any row was returned
                if not rows:
                    print(f"No data found for library: {library}")
                    return None

                # Get the single tuple from the list of rows
                row_tuple = rows[0]

                rowsTitle = [
                    'OBJECT_COUNT',
                    'LIBRARY_SIZE',
                    'LIBRARY_SIZE_COMPLETE  ',
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

        except Exception as e:
            print(f"An error occurred while fetching data: {e}")
            return None

    # def call_qcmdexec(self, command_str):
    #     """
    #     Executes a command on the IBM i using the QCMDEXC stored procedure.
    #
    #     Args:
    #         command_str (str): The command string to execute (e.g., "CRTSAVF FILE(MYLIB/MYSAVF)").
    #     """
    #     if not isinstance(command_str, str) or not command_str:
    #         raise ValueError("A non-empty string command is required.")
    #
    #     try:
    #         with self.conn.cursor() as cursor:
    #             # QCMDEXC requires the command string and its length as a decimal
    #             cursor.execute("CALL QSYS.QCMDEXC(?, ?)", (command_str, len(command_str)))
    #             print(f"Command executed successfully: {command_str}")
    #     except Exception as e:
    #         print(f"An error occurred while executing command: {e}")
    #         self.conn.rollback()
    #     else:
    #         self.conn.commit()