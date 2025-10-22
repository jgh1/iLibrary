# Troubleshooting

ODBC connection fails
- Check DB_DRIVER string matches your installed driver exactly (e.g., {IBM i Access ODBC Driver}).
- Verify host, user, and password.
- Confirm the IBM i allows remote database connections from your network.
- Test with a minimal pyodbc.connect using the same connection string.

SAVLIB permissions issues
- Ensure your user profile has authority to the library and to run SAVLIB.
- If saving to IFS (remPath), verify directory exists and user has R/W permissions.

SFTP/SSH errors
- Ensure SSH service is running on the IBM i (port 22 by default).
- If a non-standard port is used, pass port= in saveLibrary.
- Validate credentials; the library uses the same user/password as the DB connection for SSH.

File not found or download failed
- Confirm saveFileName and library are correct and within 10 characters where applicable.
- Ensure remPath is writable and localPath exists on your machine.

Long-running operations
- Large libraries can take time to save and transfer. Consider network stability and available disk space.

Still stuck?
- Enable additional logging around your calls.
- Open an issue with error messages and environment details (driver version, OS, Python version).
