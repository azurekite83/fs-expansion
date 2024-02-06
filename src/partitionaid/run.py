import re, subprocess
from .helpers import fetch_element, parse_table, get_columns, check_for_space, execute_command

def grow_partition(partition, partition_increase):
    print("Placeholder")

def run_program(arguments):
    #find what partitions mount point is
    #Initially I thought that umount syntax
    #required you to provide the mountpoint to unmount
    
    #I was mistaken. I don't feel like deleting this code though.
    
    #TODO: Add functionality to close any open processes if mount point is active
    #      -Make get_column functions use named fields and not magic numbers
    lsblk_table = parse_table("lsblk -b --list -o +START")
    df_table = parse_table("df -B 1M")

    lsblk_parsed = get_columns(lsblk_table, [0, 3, 5, 6, 7])
    df_parsed = get_columns(df_table, [0, 3])

    partition = arguments["partition"].removeprefix("/dev/")

    #To remember for when we remount
    mountpoint_of_partition = fetch_element(lsblk_parsed, 0, 6, partition)
    type_of_partition = fetch_element(lsblk_parsed, 0, 5, partition)

    
    #If they opted for an increase in partition size

    #There is a ton of types that lsblk can output
    #Right now basic functionality only supports lvm and part

    if arguments["grow"] != None and type_of_partition == "part":
        #Compare size increase to space available 
        #Note: This is using unallocated space at the end of the device to move partitions,
        #but this can also be done if one of the partitions has enough space as well

        #TODO: Add functionality to search through partitions if there is not enough unallocated space
        #       -Add regex generation depending on type of partition

        #See where partitions placement is in filesystem
        partition_number_regex = re.compile("[0-9]{1}")
        device_regex = re.compile("sd[a-z]{1}")

        partition_number_found = partition_number_regex.search(partition)
        device_found = device_regex.search(partition)

        if partition_number_found == None or device_found == None:
            print("Invalid argument for partition. Aborting...")
            exit(1)
        else:
            partition_number_found = partition_number_found.group()
            device_found = device_found.group()
        
        #check if there is enough space
        available_space = (fetch_element(lsblk_parsed, 0, 3, device) / (1024**2)) - fetch_element(df_parsed, 0, 3, partition)
        is_space_available = check_for_space(available_space, arguments["grow"]) 

        if not is_space_available:
            print("Not enough space for operation. Aborting...")
            exit(1)
        
        
        #Find highest partition number
        highest_partition = None
        
        for row in lsblk_parsed:
            if device_found in row[0]:
                current_partition_number = partition_number_regex.search(row[0]).group()

                if current_partition_number > partition_number_found:
                    highest_partition = current_partition_number

        for i in range(highest_partition, partition_number_found, -1):
            #Unmount partitions
            #Using -l flag for lazy unmount just in case there are
            #any processes still running on the partition
            partition_start_sector = int(fetch_element(lsblk_parsed, 0, 7, partition))
            new_partition_start = partition_start_sector + arguments["grow"]
            #Size of partition in Mib
            size_of_partition = int(fetch_element(lsblk_parsed, 0, 3, partition)) / (1024 ** 2)
            
            #If --backup is included
            if arguments["backup"] == True:
                execute_command(f"sfdisk --dump {arguments['partition'] > part.dump") 

            execute_command("umount -l {partition}")
        
            #Delete partition
            execute_command("sfdisk --delete {device_found}{i}")
            
            #Create partition with adjusted start and end blocks
            execute_command(f"echo -e 'size={size_of_partition}M, start={partition_start_sector}M' | sfdisk {arguments['partition']")
            #Adjust start and end blocks
        
        #Begin moving partitions

         
    
                    
    elif type_of_partition == "lvm":
        #Do logical partition things
        print("placeholder")
    else:
        print("Type of partition not currently supported. Aborting...")
        exit(1)

