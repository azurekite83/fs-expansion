import subprocess, os, csv
from os import path

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


def check_binary_exists(binary_required):
    #see if sfdisk util exists
    sub_paths = os.getenv("PATH").split(":")

    for directory in sub_paths:
        if path.exists(directory + "/" + binary_required):
            return True

    return False

def find_distro_commands(distro_id):
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

        commands = find_distro_commands(distro_id)
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

            commands = find_distro_commands(distro_id)
            package_retrieval = retrieve_packages(commands, binary)
            if package_retrieval == False:
                exit(1)

        else:
            print("Unable to identify distro, aborting...")
            exit(1)

