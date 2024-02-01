import subprocess

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

