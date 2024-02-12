import re
from partitionaid.core.utils import fetch_element, parse_table, get_columns, execute_command
from partitionaid.core.check_environment import check_binary_exists, install_binary
from partitionaid.operations.grow_partition import grow_physical_partition
from partitionaid.operations.check_space import check_for_space

def run_program(arguments):

    #check that necessary binaries exist
    #Side note:
    #   util-linux encompasses all necessary binaries for this program
    #So honestly the whole necessary_binaries thing is useless
    #If I finish making this script I'm gonna have to improve
    #a lot of stuff. And make a better way to query for missing
    #packages
    
    #TODO: -Make file for dependencies instead of dictionary 

    necessary_binaries = {"sfdisk": "fdisk", "lsblk": "util-linux"}

    for binary in necessary_binaries:
        if check_binary_exists(binary) == False:
           install_binary(necessary_binaries[binary])
        
    #TODO: -Make get_column functions use named fields and not magic numbers 
    
    lsblk_table = parse_table("lsblk -b --list -o +START,FSAVAIL")

    lsblk_parsed = get_columns(lsblk_table, [0, 3, 5, 6, 7, 8])

    partition = arguments["partition"].removeprefix("/dev/")

    #To remember for when we remount
    type_of_partition = fetch_element(lsblk_parsed, 0, 5, partition)

    #If they opted for an increase in partition size

    #There is a ton of types that lsblk can output
    #Right now basic functionality only supports lvm and part

    if arguments["grow"] != None and type_of_partition == "part":
        grow_physical_partition(lsblk_parsed, arguments["partition"], arguments["grow"], arguments["backup"])
        
    elif type_of_partition == "lvm":
        #Do logical partition things
        print("placeholder")
    else:
        print("Type of partition not currently supported. Aborting...")
        exit(1)

