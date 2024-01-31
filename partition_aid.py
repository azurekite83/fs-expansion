import sys, os, argparse, csv, subprocess, re
from os import path

#Use sfdisk to give commands to change partitions
#Arguments:
#   -logical/physical partition
#   -which partition
#   -shrink or grow partition
#   -backup before action

def parse_arguments(args):
    parser = argparse.ArgumentParser(description="A wrapper around bash scripts to simplify partition changes")
    parser.add_argument("partition", help="Ex. /dev/sda{1-5} or /dev/mapper/")
    parser.add_argument("--backup", "-b", action="store_true", help="Directory to store backup to.")


    size_changes = parser.add_argument_group("CHANGING PARTITION SIZE")

    size_change_group = size_changes.add_mutually_exclusive_group(required=True)
    size_change_group.add_argument("--grow", help="--grow <size>{M, G}", type=str, metavar="<size>")
    size_change_group.add_argument("--shrink", help="--shrink <size>{M, G}", type=str, metavar="<size>")
   
    
    argument_list = parser.parse_args(args[1:])
    return argument_list

def check_binary_exists(binary_required):
    #see if sfdisk util exists
    sub_paths = os.getenv("PATH").split(":")

    for directory in sub_paths:
        if path.exists(directory + "/" + binary_required):
            return True

    return False

def retrieve_packages(command_list, package_to_retrieve):
    if len(command_list) > 1:
        first_command = command_list[0].split()
        first_command.append(package_to_retrieve)

        second_command = command_list[1].split()
        second_command.append(package_to_retrieve)

        with subprocess.run(first_command, capture_output=True, text=True) as status_one:
            if status_one.returncode != 0:
                print(status_one.stderr)
                print("Trying different command...")

                with subprocess.run(second_command, capture_output=True, text=True) as status_two:
                    if status_two.returncode != 0:
                        print(status_two.stderr)
                        print("Package retrieval failed, aborting...")
                        return False

            else:
                return True

    elif len(command_list) == 1:
        command = command_list[0].split()
        command.append(package_to_retrieve)
        command_output = subprocess.run(command)

        if command_output.returncode != 0:
            print("Package retrieval failed, aborting...")
            return False
    else:
        print("Error in finding package manager, aborting...")
        return False

    return True

def fetch_commands(distro_id):
    with open("pkg-mng.csv", "r") as csv_file:
        csv_parsed = csv.DictReader(csv_file)

        for row in csv_parsed:
            if row["distribution"] == distro_id:
                possible_commands = row["syntax"].split(",")
                return possible_commands



def install_binary(binary):
   #Check which package manager is being used
    """
        Currently having to manually put in
        what package managers distros use in
        a csv file.
        Will continue to be trash until I decide
        this is worth being expanded upon.
    """

    #See if lsb-release is installed first,
    #easiest thing to do.
    lsb_exists = check_binary_exists("lsb_release")
            
    if lsb_exists:
        lsb_output = subprocess.run(["lsb_release", "-i"], text=True, capture_output=True)

        distro_id = lsb_output.stdout.lower().removeprefix("distributor id:").strip()

        commands = fetch_commands(distro_id)
        package_retrieval = retrieve_packages(commands, binary)
        
        if package_retrieval == False:
            exit(1)
    else:
        #If lsb_release doesn't exist
        #Only need os-release to determine distro

        if path.exists("/etc/os-release"):
            distro_id = None

            with open("/etc/os-release", "r") as os_info:
                for line in os_info:
                    if "ID=" in line:
                        distro_id = line.removeprefix("ID=").strip()
                        break

            commands = fetch_commands(distro_id)
            package_retrieval = retrieve_packages(commands, binary)
            if package_retrieval == False:
                exit(1)

        else:
            print("Unable to identify distro, aborting...")
            exit(1)

def parse_table(command):
    parsed_command = command.split()
    row_data = None

    try:
        command_results = subprocess.run(parsed_command, capture_output=True, text=True).stdout.splitlines()
        row_data = [line.split() for line in command_results]
        break
    except:
        print("Command execution failed.")

    return row_data

def get_columns(table, column_numbers):
    columns_wanted = []
    index = 0

    for row in table:
        columns_wanted.append([])
        for number in column_numbers:
            #For lsblk, some partitions don't have mountpoints
            #If they do the row length is 7
            try:
                columns_wanted[index].append(row[number])
                break
            except:
                columns_wanted[index].append(None)
        index += 1


def run(arguments):
    #find what partitions mount point is
    #Initially I thought that umount syntax
    #required you to provide the mountpoint to unmount
    
    #I was mistaken. I don't feel like deleting this code though.
    
    #TODO: Add functionality to close any open processes if mount point is active
    lsblk_table = parse_table("lsblk")
    df_table = parse_table("df -B 1M")

    partition = arguments["partition"].removeprefix("/dev/")
    selected_mountpoints = get_columns(lsblk_table, [0, 5, 6])
    filesystem_space = get_columns(df_table, [3])

    #umount partition

    #To remember for when we remount
    mountpoint_of_partition = None
    type_of_partition = None

    #See where partitions placement is in filesystem
    partition_number_regex = re.compile("[0-9]{1}")
    device_regex = re.compile("sd[a-z]{1}")

    partition_number_found = partition_number_regex.search(arguments["partition"]).group()
    device_found = device_regex.search(arguments["partition"]).group()

    #If they opted for an increase in partition size
    #check if there is enough space
    
    if arguments["grow"] != None:
       #Compare size increase to space available 

    #TODO: Turn this loop into a function if it gets repeated
    for row in selected_mountpoints:
        if arguments["partition"] in row[0] and row[6] != None:
            mountpoint_of_partition = row[6]
            type_of_partition = row[5]
        else:
            print("Partition not mounted or invalid partition. Aborting...")
            exit(1)

    #There is a ton of types that lsblk can output
    #Right now basic functionality only supports lvm and part
    if type_of_partition == "part":
        #Unmount partition
        #Using -l flag for lazy unmount just in case there are
        #any processes still running on the partition
        unmount_status = subprocess.run(["umount", "-l", arguments["partition"]], capture_output=True, text=True)
        
        if unmount_status.returncode != 0:
            print(unmount_status.stderr)
            print("Aborting...")
            exit(1)

        
        #Find highest partition number
        highest_partition = None
        
        for row in selected_mountpoints:
            if device in row[0]:
                current_partition_number = partition_number_regex.search(row[0]).group()

                if current_partition_number > partition_number_found:
                    highest_partition = current_partition_number

    elif type_of_partition == "lvm":
        #Do logical partition things
    else:
        print("Type of partition not currently supported. Aborting...")
        exit(1)


def main():

    print("""
            WARNING: IF THERE ARE ANY RUNNING PROCESSES IN THE PARTITION YOU ARE TRYING TO CHANGE
            YOU **MUST** CLOSE ANY ACTIVE PROCESSES OTHERWISE THIS COULD POTENTIALLY MESS UP YOUR
            PARTITION
          """)

    user_acknowledgement = input("Do you still want to continue? (yes/y/no/n): ")

    if user_acknowledgement == "yes" or user_acknowledgement == "y":
        break
    else:
        exit(0)

    uid = os.getuid()

    #First, check if running as root
    if uid != 0:
        print("This program needs elevated privileges, run as root.")
        exit(1)
    #gather arguments 
    argument_list = parse_arguments(sys.argv)
    
    partition = argument_list.partition
    backup = argument_list.backup
    partition_increase = argument_list.grow
    partition_decrease = argument_list.shrink

    #check that necessary binaries exist
    #Side note:
    #   util-linux encompasses all necessary binaries for this program
    #So honestly the whole necessary_binaries thing is useless
    #If I finish making this script I'm gonna have to improve
    #a lot of stuff. And make a better way to query for missing
    #packages
    
    #TODO: -Change program to install util-linux if it doesn't have it
    #      -Make file for dependencies instead of dictionary 
    necessary_binaries = {"sfdisk": "fdisk", "lsblk": "util-linux", "df": "coreutils"}

    for binary in necessary_binaries:
        if check_binary_exists(binary) == False:
           install_binary(necessary_binaries[binary])

    arguments_to_run = {"partition": partition, "backup": backup, "grow": partition_increase, "shrink": partition_decrease} 

    run(arguments_to_run)
    
if __name__ == "__main__":
    main()
