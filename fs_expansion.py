import sys, os, argparse

#Use sfdisk to give commands to change partitions
#Arguments:
#   -lvm/physical partition
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

def main():
    uid = os.getuid()

    #First, check if running as root
    if uid != 0:
        print("This program needs elevated privileges, run as root.")
        exit(1)
    
    argument_list = parse_arguments(sys.argv)
    
    partition = argument_list.partition
    backup = argument_list.backup
    partition_increase = argument_list.grow
    partition_decrease = argument_list.shrink


if __name__ == "__main__":
    main()
