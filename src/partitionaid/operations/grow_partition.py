from partitionaid.core.utils import execute_command, fetch_element
from partitionaid.operations.check_space import check_for_space
import re

def generate_sub_args(table, partition, partition_increase):
    #TODO: turn devices found into a list and check to see that the list isn't empty
    #modify partition number regex to account for nvme and other drive naming conventions
    partition_number_regex = re.compile("[0-9]{1}")
    device_regex_list = [
            re.compile("sd[a-z]{1}"),
            re.compile("hd[a-z]{1}"), 
            re.compile("nvme[0-5]{1}n[0-5]{1}"),
            re.compile("\w+-\w+"),
            re.compile("\w+")
            ]
    size_increase_regex = re.compile("[0-9]+")

    partition_number_found = partition_number_regex.search(partition)
    device_found = None
    size_increase_found = size_increase_regex.match(partition_increase)
    highest_partition = None
    available_space = (int(fetch_element(table, 0, 8, device_found)) / (1024**2)) 
    byte_suffix = partition_increase.removeprefix(size_increase_found)

    for i, regex_object in enumerate(device_regex_list):
        regex_object.match(partition)
        if regex_object is None:
            continue
        else:
            device_found = regex_object.group()
            break

    partition_number_found = partition_number_found.group()
    size_increase_found = size_increase_found.group()

    #Find highest partition number
    for row in table:
        if device_found in row[0]:
            current_partition_number = partition_number_regex.search(row[0]).group()

            if current_partition_number > partition_number_found:
                highest_partition = current_partition_number
    

    sub_arguments = {
            "partition_number_found": partition_number_found,
            "physical_device_found": physical_device_found,
            "size_increase_number": size_increase_found,
            "highest_partition": highest_partition,
            "available_space": available_space,
            "byte_suffix": byte_suffix
            }
    return sub_arguments


def grow_physical_partition(table, partition, partition_increase, backup):
    #Compare size increase to space available 
    #Note: This is using unallocated space at the end of the device to move partitions,
    #but this can also be done if one of the partitions has enough space as well

    #TODO: Add functionality to search through partitions if there is not enough unallocated space
    #       -Test on VM because I don't know what order partitions are created in

    #See where partitions placement is in filesystem
    
    sub_arguments = generate_sub_args(table, partition, partition_increase)

    if sub_arguments == False:
        print("Error in sub_arguments(), aborting...")
        exit(1)
    
        
    #check if there is enough space
    is_space_available = check_for_space(sub_arguments["available_space"], partition_increase) 

    if is_space_available is False:
        print("Not enough space for operation. Aborting...")
        exit(1)

    for i in range(sub_arguments["highest_partition"], sub_arguments["partition_number_found"], -1):
        current_partition = f"{sub_arguments['physical_device_found']}{i}"
        partition_start_sector = int(fetch_element(table, 0, 7, current_partition)) / (1024 ** 2)
        current_mountpoint = fetch_element(table, 0, 6, current_partition)

        if sub_arguments["byte_suffix"] == "G" or sub_arguments["byte_suffix"] == "g":
            sub_arguments["size_increase_number"] *= 1024 

        #New partition start sector
        new_partition_start = partition_start_sector + sub_arguments["size_increase_number"]
        #Size of partition in Mib
        size_of_partition = (int(fetch_element(table, 0, 3, current_partition)) / (1024 ** 2))
            
        if current_partition == partition:
            total_size_increase = size_of_partition + sub_arguments["size_increase_number"]
            execute_command(f"umount -l {partition}")
            execute_command(f"sfdisk --delete {partition}")
            execute_command(f"echo -e 'size={total_size_increase}M start={partition_start_sector}M' | sfdisk {partition}")
            execute_command(f"mount {partition} {current_mountpoint}")
        else:        
            #If --backup is included
            if backup == True:
                execute_command(f"sfdisk --backup-pt-sectors {sub_arguments['physical_device_found']}") 
                #Unmount partitions

                #Using -l flag for lazy unmount just in case there are
                #any processes still running on the partition
                execute_command(f"umount -l /dev/{current_partition}")
        
                #Delete partition
                execute_command(f"sfdisk --delete {current_partition}")
            
                #Create partition with adjusted start and end blocks
                execute_command(f"echo -e 'size={size_of_partition}M, start={new_partition_start}M' | sfdisk /dev/{sub_arguments['physical_device_found']}")

                #Remount partition
                execute_command(f"mount /dev/{current_partition} {current_mountpoint}")

def grow_logical_partition(table, partition, partition_increase, backup):
    #Assumes that user has already accounted for size of physical partition and extends logical partition in volume group

    #TODO: Separate function into accounting for physical volumes, and volume groups, not just logical volumes
    #      Don't only check for space in physical partition, but check physical volume assigned as well
    #      Figure out how to return row in table with right info 

    # check to see if there is space
    sub_arguments = generate_sub_args(table, partition, partition_increase)

    if sub_arguments == False:
        print("Error in sub_arguments(), aborting...")
        exit(1)
    
    #Check for space
    is_space_available = check_for_space(sub_arguments["available_space"], partition_increase)

    if is_space_available == False:
        print("Not enough space for operation. Aborting...")
        exit(1)

    # Resize logical volume to fit physical volume
    execute_command(f"lvresize -L +{partition_increase} --resizefs {partition}")
    
    return False
