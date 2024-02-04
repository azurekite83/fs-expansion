import re, subprocess
from helpers import fetch_element, parse_table, get_columns, check_for_space

def grow_partition(partition, partition_increase):
    print("Placeholder")

def run_program(arguments):
    #find what partitions mount point is
    #Initially I thought that umount syntax
    #required you to provide the mountpoint to unmount
    
    #I was mistaken. I don't feel like deleting this code though.
    
    #TODO: Add functionality to close any open processes if mount point is active
    lsblk_table = parse_table("lsblk -b")
    df_table = parse_table("df -B 1M")

    lsblk_parsed = get_columns(lsblk_table, [0, 3, 5, 6])
    df_parsed = get_columns(df_table, [0, 3])

    partition = arguments["partition"].removeprefix("/dev/")

    #To remember for when we remount
    mountpoint_of_partition = fetch_element(lsblk_parsed, 0, 6, partition)
    type_of_partition = fetch_element(lsblk_parsed, 0, 5, partition)

    
    #If they opted for an increase in partition size

    #There is a ton of types that lsblk can output
    #Right now basic functionality only supports lvm and part

    #Start and end sector list for during operations
    start_and_end_sectors = []
    
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
        is_space_available = check_for_space(lsblk_parsed, df_parsed, device_found, partition, arguments["grow"]) 

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

            unmount_status = subprocess.run(["umount", "-l", f"{partition}"], capture_output=True, text=True)
        
            if unmount_status.returncode != 0:
                print(unmount_status.stderr)
                print("Aborting...")
                exit(1)

            #Delete partition
            removal_status = subprocess.run(["sfdisk", "--delete", f"{device_found}", f"{i}"], capture_output=True, text=True)
            
            if removal_status.returncode != 0:
                print(removal_status.stderr)
                print("Aborting...")
                exit(1)
                
            #Remount with adjusted start and end blocks
            
        
        #Begin moving partitions

         
    
                    
    elif type_of_partition == "lvm":
        #Do logical partition things
        print("placeholder")
    else:
        print("Type of partition not currently supported. Aborting...")
        exit(1)

