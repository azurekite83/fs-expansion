import sys, os, argparse, csv
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
        if path.exists(directory + binary_required):
            return True

    return False

def install_binary(binary):
   #Check which package manager is being used
    """
        Currently having to manually put in
        what package managers distros use in
        a csv file.
        Will continue to be trash until I decide
        this is worth being expanded upon.
    """
    with open("pkg-mng.csv", "r") as csv_file:
        csv_parsed = csv.DictReader(csv_file)

        for row in csv_parsed:
            print(row)

   #After package manager is detected run command
def run(necessary_binaries, arguments):
    print(necessary_binaries)
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
    necessary_binaries = {"sfdisk": False, "lsblk": False}

    for binary in necessary_binaries:
        necessary_binaries[binary] = check_binary_exists(binary) 
        if necessary_binaries[binary] == False:
            install_binary(binary)
    
if __name__ == "__main__":
    main()
