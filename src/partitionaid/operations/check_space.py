import re

def check_for_space(available_space, size_increase): 
    size_change_regex = re.compile("[0-9]+")
    size_change_found = size_change_regex.match(size_increase).group()
    size_change_actual = int(size_change_found)

    try:
        byte_suffix = size_increase.removeprefix(size_change_found)

        if byte_suffix == "G" or byte_suffix == "g":
            size_change_actual *= 1024
        elif byte_suffix == "K" or byte_suffix == "k":
            size_change_actual /= 1024
        elif byte_suffix != "M" and byte_suffix != "m":
            print("Byte suffix not currently supported. Aborting...")
            return False
    except:
        print("Invalid input. Aborting...")
        return False

    if size_change_actual > available_space:
        print("Not enough space to perform operation. Aborting...")
        return False
    else:
        return True

