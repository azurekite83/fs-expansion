import sys, os, argparse
from partitionaid.core.run import run_program
from os import path

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


def cli():

    print("""
            WARNING: IF THERE ARE ANY RUNNING PROCESSES IN THE PARTITION YOU ARE TRYING TO CHANGE
            YOU **MUST** CLOSE ANY ACTIVE PROCESSES OTHERWISE THIS COULD POTENTIALLY MESS UP YOUR
            PARTITION
          """)

    user_acknowledgement = input("Do you still want to continue? (yes/y/no/n): ")

    #TODO: Improve *this*
    if user_acknowledgement == "yes" or user_acknowledgement == "y":
        print("Continuing...")
    else:
        exit(0)

    uid = os.getuid()

    #First, check if running as root
    if uid != 0:
        print("This program needs elevated privileges, run as root.")
        exit(1)
    #gather arguments 
    namespace_argument_list = parse_arguments(sys.argv)

    partition = namespace_argument_list.partition
    grow = namespace_argument_list.grow
    shrink = namespace_argument_list.shrink
    backup = namespace_argument_list.backup

    argument_list = {"partition": partition, "grow": grow, "shrink": shrink, "backup": backup}

    run_program(argument_list)

    
if __name__ == "__main__":
    cli()
