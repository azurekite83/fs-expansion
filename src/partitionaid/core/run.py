import re
from partitionaid.core.utils import fetch_element, parse_table, get_columns, execute_command
from partitionaid.core.check_environment import check_binary_exists, install_binary
from partitionaid.operations.grow_partition import grow_physical_partition, grow_logical_partition
from partitionaid.operations.check_space import check_for_space

def run_program(arguments):

    #check that necessary binaries exist
    
    #TODO: -Make file for dependencies instead of dictionary 

    necessary_binaries = {"sfdisk": "fdisk", "lsblk": "util-linux", "pvdisplay": "lvm2"}

    for binary in necessary_binaries:
        if check_binary_exists(binary) == False:
           install_binary(necessary_binaries[binary])
        
    #TODO: -Make get_column functions use named fields and not magic numbers 
    
    lsblk_table = parse_table("lsblk -b --list -o +START,FSAVAIL")

    lsblk_parsed = get_columns(lsblk_table, [0, 3, 5, 6, 7, 8])

    partition = arguments["partition"].removeprefix("/dev/")

    type_of_partition = fetch_element(lsblk_parsed, 0, 5, partition)

    #If they opted for an increase in partition size

    #There is a ton of types that lsblk can output
    #Right now basic functionality only supports lvm and part

    if arguments["grow"] != None and type_of_partition == "part":
        grow_physical_partition(lsblk_parsed, arguments["partition"], arguments["grow"], arguments["backup"])

    elif type_of_partition == "lvm" and arguments["grow"] != None:
        grow_logical_partition()

    else:
        print("Type of partition not currently supported. Aborting...")
        exit(1)

