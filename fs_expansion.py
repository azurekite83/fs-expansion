import sys, os, argparse, csv, subprocess
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

        if subprocess.run(first_command).returncode != 0:
            print("First package manager failed, trying alternate...")
            if subprocess.run(second_command).returncode != 0:
                print("Package retrieval failed, aborting...")
                return False
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
        package_retrieval_result = retrieve_packages(commands, binary)
        
        if package_retrieval_result == False:
            exit(1)

        
   #After package manager is detected run command
def run(arguments):
    print(arguments)

def main():
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
    necessary_binaries = {"fdisk": False, "util-linux": False}

    for binary in necessary_binaries:
        necessary_binaries[binary] = check_binary_exists(binary) 

        if necessary_binaries[binary] == False:
           install_binary(binary)
           necessary_binaries[binary] = True

    run([partition, backup, partition_increase, partition_decrease])
    
if __name__ == "__main__":
    main()
