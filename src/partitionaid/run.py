import re
from src.partitionaid.helpers import fetch_element, parse_table, get_columns, check_for_space, execute_command
from src.partitionaid.operations import grow_physical_partition


def run_program(arguments):
        
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

