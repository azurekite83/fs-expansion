from src.partitionaid.environment import check_binary_exists, install_binary, fetch_commands
import pytest, sys

# *** def check_binary_exists(): ***
@pytest.mark.skipif(sys.platform.startswith("win32") == True, reason="Not currently compatible with Windows.")
def test_existing_binary():
    #Should always pass on most linux systems
    assert check_binary_exists("ls") == True

@pytest.mark.skipif(sys.platform.startswith("win32") == True, reason="Not currently compatible with Windows.")
def test_non_existent_binary():
    assert check_binary_exists("pig") == False


# *** def fetch_commands(): ***

@pytest.mark.skipif(sys.platform.startswith("win32") == True, reason="Not currently compatible with Windows.")
def test_distro_arch(monkeypatch):
    monkeypatch.chdir("src/partitionaid")
    
    assert fetch_commands("arch") == ["pacman -S"]
# *** def install_binary(): ***

@pytest.mark.skipif(sys.platform.startswith("win32") == True, reason="Not currently compatible with Windows.")
def test_binary_install():
    #Very limited currently, if this fails on
    # your system, make sure to have included binaries needed.
    # Refer to __main__.py

    assert install_binary("neofetch") == None

