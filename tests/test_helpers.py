from helpers import parse_table, get_columns, fetch_element, check_for_space, execute_command
import subprocess
import pytest

def test_execute_command_pass():
    passing_command = "lsblk -b"
    
    assert execute_command(passing_command) == None

def test_execute_command_no_whitespace():
    failing_command = "jibberishsh"

    with pytest.raises(Exception):
        execute_command(failing_command)

