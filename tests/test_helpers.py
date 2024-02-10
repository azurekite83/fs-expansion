from src.partitionaid.helpers import parse_table, get_columns, fetch_element, check_for_space, execute_command
import subprocess
import pytest

#   *** def execute_command(): ***

def test_pass_a():
    passing_command = "lsblk -b"
    
    assert execute_command(passing_command) is None

def test_invalid_command():
    failing_command = "jibberishsh"

    with pytest.raises(Exception):
        execute_command(failing_command)

def test_no_whitespace():
    failing_command = "lsblk-b"

    with pytest.raises(Exception):
        execute_command(failing_command)

def test_empty():
    with pytest.raises(Exception):
        execute_command("")

def test_invalid_syntax():
    with pytest.raises(Exception):
        execute_command("lsblk -listing")

# *** def check_for_space(): ***

def test_pass_b():
    assert check_for_space(5000, "500M") is True

def test_no_space():
    assert check_for_space(50, "500M") is False

def test_wrong_suffix():
    assert check_for_space(5000, "500P") is False

def test_case_pass():
    cases = ["200G", "200g", "200K", "200k"]
    results = []


    for case in cases:
        results.append(check_for_space(500000, case))

    assert results == [True, True, True, True]

def test_case_fail():
    cases = ["200x", "200p", "200t", "200X", "200P", "200T"]
    results = []

    for case in cases:
        results.append(check_for_space("500000", case))

    assert results == [False, False, False, False, False, False]

def test_invalid_size_increase():
    with pytest.raises(Exception):
        check_for_space("500000", "piglet")

# *** def parse_table(): ***

def test_pass_c():
    row_test = ["NAME", "MAJ:MIN", "RM", "SIZE", "RO", "TYPE", "MOUNTPOINTS"]
    table = parse_table("lsblk -l")

    assert row_test in table 

def test_command_fail(capsys):
    with pytest.raises(SystemExit):
        parse_table("lsbak -list")

# *** def get_columns(): *** 

def test_pass_d():
    data = [["a", "b"], ["1 2", "3 4"]]

    assert get_columns(data, [0]) == [["a"], ["1 2"]]

def test_none_in_table():
    data = [["a", "b", "c"], ["1 2", "3 4"]]

    assert get_columns(data, [2]) == [["c"], [None]]


# *** def fetch_element(): ***

def test_pass_e():
    data = [["a", "b", "c"],
            ["1 2", "3 4", "5 6"]]

    assert fetch_element(data, 0, 2, "1 2") == "5 6"

def test_none_in_row():
    data = [["a", "b", "c", "d"],
            ["1 2", "3 4", "5 6"]]

    assert fetch_element(data, 0, 3, "1 2") is None








