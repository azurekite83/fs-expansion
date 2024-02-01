import subprocess

def parse_table(command):
    parsed_command = list(command.split())
    row_data = None

    try:
        command_results = subprocess.run(parsed_command, capture_output=True, text=True).stdout.splitlines()
        row_data = [line.split() for line in command_results]
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
            except:
                columns_wanted[index].append(None)
        index += 1

    return columns_wanted

def fetch_element(table, search_column, wanted_column, query):
    result = None

    for row in table:
        if query in row[search_column]:
            try:
                result = row[wanted_column]
            except:
                return None
           

    return result

def check_for_space(lsblk_parsed, df_parsed, partition, device, size_increase, regex_result): 
    available_space = (fetch_element(lsblk_parsed, 0, 3, device) / (1024**2)) - fetch_element(df_parsed, 0, 3, partition)

    size_change_regex = re.compile("[0-9]+")
    size_change_found = size_change_regex.match(size_increase)

    try:
        size_change_found = regex_result.group()
        byte_suffix = size_increase.removeprefix(size_change_found)

        if byte_suffix == "G" or byte_suffix == "g":
            size_change_found *= 1024
        elif byte_suffix == "K" or byte_suffix == "k":
            size_change_found /= 1024
        else:
            print("Byte suffix not currently supported. Aborting...")
            return False
    except:
        print("Invalid size change. Aborting...")
        return False


