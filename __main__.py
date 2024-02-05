import sys, os
from src.partitionaid import args
from src.partitionaid import environment
from src.partitionaid import run

from os import path

def main():

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
    argument_list = args.parse_arguments(sys.argv)
    
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
        if environment.check_binary_exists(binary) == False:
           environment.install_binary(necessary_binaries[binary])

    arguments_to_run = {"partition": partition, "backup": backup, "grow": partition_increase, "shrink": partition_decrease} 

    run.run_program(arguments_to_run)
    
if __name__ == "__main__":
    main()
