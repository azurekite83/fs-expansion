import subprocess, sys 

def parse_table(command):
    parsed_command = list(command.split())
    row_data = None

    try:
        command_results = subprocess.run(parsed_command, capture_output=True, text=True).stdout.splitlines()
        row_data = [line.split() for line in command_results]
    except:
        print("This should never happen.")
        sys.exit(1)

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

#Change execute_command to have better error handling

def execute_command(command):
    command_list = list(command.split())
    command_status = subprocess.run(command_list, capture_output=True, text=True, check=True)

    try:
        command_status.check_returncode()
    except:
        print(f"Failed command execution with: {command_status.stderr}") 
        print("Aborting...")
        sys.exit(1)
        
