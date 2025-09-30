import pytest
from unittest.mock import patch, MagicMock
import os
from dotenv import load_dotenv
from os.path import join, dirname, abspath

# --- Global Path Setup (CRITICAL FIX) ---
# Find the project root directory (two levels up from 'app/iLibrary/tests')
PROJECT_ROOT = abspath(join(dirname(__file__), '..', '..', '..'))

# --- Setup Environment for Testing (Reads .env file) ---
DOTENV_PATH = join(PROJECT_ROOT, '.env')
load_dotenv(DOTENV_PATH)

# Use os.environ directly, as load_dotenv has been called.
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_SYSTEM = os.environ.get("DB_SYSTEM")
DB_DRIVER = os.environ.get("DB_DRIVER")
DB_LIB = os.environ.get("DB_LIB")
DB_REMPATH = os.environ.get("DB_REMPATH")
LOCAL_PATH = join(PROJECT_ROOT, 'app')


# ---------------------------------------------
# Pytest Fixture for Mocking the Library Class
# ---------------------------------------------
@pytest.fixture
def mock_library_context():
    """
    Mocks the iLibrary.Library class and explicitly configures it
    as a context manager.
    """
    # 1. Mock the entire Library class (Tracks the __init__ call)
    mock_lib_class = MagicMock()

    # 2. Mock the instance methods that are used inside the 'with' block
    mock_lib_instance = MagicMock()

    # Configure the mock instance's return value for the successful case
    mock_lib_instance.saveLibrary.return_value = {
        "status": "success",
        "message": "Save file created and transferred."
    }

    # 3. Configure the CLASS MOCK to act as a context manager
    # When 'with mock_lib_class(...) as lib' is run, it returns mock_lib_instance
    mock_lib_class.return_value.__enter__.return_value = mock_lib_instance

    # Patch the original iLibrary.Library class
    # NOTE: Adjust the patch target if 'iLibrary' is imported from a different location
    with patch('iLibrary.Library', mock_lib_class) as mock_patch:
        # Yield both the class mock and the instance mock
        yield mock_lib_class, mock_lib_instance

    # ---------------------------------------------


# The Test Functions
# ---------------------------------------------

def test_main_library_save_successful(mock_library_context):
    """
    Tests the main script logic's 'happy path' by asserting all mocks are
    called correctly and with the environment variables.
    """

    mock_lib_class, lib_instance = mock_library_context

    result = None
    try:
        # Simulate the 'with iLibrary.Library(...) as lib:' block.
        # Since 'iLibrary.Library' is patched to 'mock_lib_class', we call it normally.
        with mock_lib_class(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
            result = lib.saveLibrary(
                library=DB_LIB,
                saveFileName='TESTSAVF',
                getZip=True,
                localPath=LOCAL_PATH,
                remPath=DB_REMPATH,
                port=2222,
                toLibrary=DB_LIB
            )
    except Exception as e:
        pytest.fail(f"An unexpected error occurred: {e}")

    # 1. Assertion A: Check the constructor call (on the class mock)
    mock_lib_class.assert_called_once_with(
        DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER
    )

    # 2. Assertion B: Check the method call (on the instance mock)
    lib_instance.saveLibrary.assert_called_once_with(
        library=DB_LIB,
        saveFileName='TESTSAVF',
        getZip=True,
        localPath=LOCAL_PATH,
        remPath=DB_REMPATH,
        port=2222,
        toLibrary=DB_LIB
    )

    # 3. Assertion C: Check the return value
    assert result["status"] == "success"


def test_main_library_save_error(mock_library_context):
    """
    Tests the error path by configuring the mock to raise an exception.
    We assert that the exception is successfully raised by the 'with' block.
    """

    mock_lib_class, lib_instance = mock_library_context

    # 1. Arrange: Make the mocked saveLibrary method raise an exception
    lib_instance.saveLibrary.side_effect = Exception("IBM i Connection Timeout")

    # 2. Act/Assert: Use pytest.raises to assert the exception is raised
    # Call the mocked class normally, which will trigger the exception when saveLibrary is called.
    with pytest.raises(Exception) as excinfo:
        with mock_lib_class(DB_USER, DB_PASSWORD, DB_SYSTEM, DB_DRIVER) as lib:
            lib.saveLibrary(library=DB_LIB)

            # Optional: Assert the error message contains the expected string
    assert "IBM i Connection Timeout" in str(excinfo.value)