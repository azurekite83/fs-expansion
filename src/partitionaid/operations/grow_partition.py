from partitionaid.core.utils import execute_command, fetch_element
from partitionaid.operations.check_space import check_for_space
import re

def grow_physical_partition(table, partition, partition_increase, backup):
    #Compare size increase to space available 
    #Note: This is using unallocated space at the end of the device to move partitions,
    #but this can also be done if one of the partitions has enough space as well

    #TODO: Add functionality to search through partitions if there is not enough unallocated space
    #       -Make regex pattern compilations better
    #       -Add regex generation depending on type of partition
    #       -Find a way to test this
    #       -Test on VM because I don't know what order partitions are created in

    #See where partitions placement is in filesystem
    partition_number_regex = re.compile("[0-9]{1}")
    device_regex = re.compile("sd[a-z]{1}")
    size_increase_regex = re.compile("[0-9]+")

    partition_number_found = partition_number_regex.search(partition)
    device_found = device_regex.search(partition)
    size_increase_found = size_increase_regex.match(partition_increase)

        
    if partition_number_found == None or device_found == None:
        print("Invalid argument for partition. Aborting...")
        exit(1)
    else:
        partition_number_found = partition_number_found.group()
        device_found = device_found.group()
        
    #check if there is enough space
    available_space = (int(fetch_element(table, 0, 8, device_found)) / (1024**2)) 
    is_space_available = check_for_space(available_space, partition_increase) 

    if is_space_available is False:
        print("Not enough space for operation. Aborting...")
        exit(1)
        
        
    #Find highest partition number
    highest_partition = None
        
    for row in table:
        if device_found in row[0]:
            current_partition_number = partition_number_regex.search(row[0]).group()

            if current_partition_number > partition_number_found:
                highest_partition = current_partition_number

    for i in range(highest_partition, partition_number_found, -1):
        current_partition = f"{device_found}{i}"
        partition_start_sector = int(fetch_element(table, 0, 7, current_partition)) / (1024 ** 2)
        current_mountpoint = fetch_element(table, 0, 6, current_partition)
        byte_suffix = partition_increase.removeprefix(size_increase_found)

        if byte_suffix == "G" or byte_suffix == "g":
            size_increase_found *= 1024 

        #New partition start sector
        new_partition_start = partition_start_sector + size_increase_found
        #Size of partition in Mib
        size_of_partition = (int(fetch_element(table, 0, 3, current_partition)) / (1024 ** 2))
            
        if current_partition == partition:
            total_size_increase = size_of_partition + size_increase_found
            execute_command(f"umount -l {partition}")
            execute_command(f"sfdisk --delete {partition}")
            execute_command(f"echo -e 'size={total_size_increase}M start={partition_start_sector}M' | sfdisk {partition}")
            execute_command(f"mount {partition} {current_mountpoint}")
        else:        
            #If --backup is included
            if backup == True:
                execute_command(f"sfdisk --dump {partition} > part.dump") 
                #Unmount partitions

                #Using -l flag for lazy unmount just in case there are
                #any processes still running on the partition
                execute_command(f"umount -l /dev/{current_partition}")
        
                #Delete partition
                execute_command(f"sfdisk --delete {current_partition}")
            
                #Create partition with adjusted start and end blocks
                execute_command(f"echo -e 'size={size_of_partition}M, start={new_partition_start}M' | sfdisk /dev/{device_found}")

                #Remount partition
                execute_command(f"mount /dev/{current_partition} {current_mountpoint}")
