from environment import check_binary_exists, install_binary

# *** def check_binary_exists(): ***

def test_existing_binary():
    #Should always pass on most linux systems
    assert check_binary_exists("ls") == True

def test_non_existent_binary():
    assert check_binary_exists("pig") == False

# *** def install_binary(): ***

def test_binary_install():
    #Very limited currently, if this fails on
    # your system, make sure to have included binaries needed.
    # Refer to __main__.py

    assert install_binary("neofetch") == None

#TODO: Figure out why install_binary() doesn't find pkg-mng.csv file
