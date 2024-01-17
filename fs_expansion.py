import sys, os, argparse

#Use sfdisk to give commands to change partitions
#Arguments:
#   -lvm/physical partition
#   -which partition
#   -shrink or grow partition
#   -backup before action

def main(args):
    uid = os.getuid()

    #First, check if running as root
    if uid != 0:
        print("This program needs elevated privileges, run as root.")
        exit(1)
    
    backup = False
    shrink = False
    grow = False
    lvm = False
    physical = False

    parser = argparse.ArgumentParser(description="A wrapper around bash scripts to simplify partition changes")
    parser.add_argument("partition", type=str, help="Ex. /dev/sda or /dev/mapper/")
    parser.add_argument("size", type=int, help="Size to shrink/grow partition when specifying --shrink/--grow flag")

    parser.add_argument("--backup", action="store_true")
    parser.add_argument("--action", choices=["grow", "shrink"], required=True)
    parser.add_argument("--type", choices=["lvm", "physical"], required=True)

    parser.parse_args(args)

if __name__ == "__main__":
    main(sys.argv)
