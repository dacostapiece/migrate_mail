import os

# Function to check if a file contains the specified phrase
def check_file(file_path, target_phrase):
    with open(file_path, 'r', encoding="utf-8", errors="ignore") as file:
        content = file.read()
        if target_phrase in content:
            return True
        else:
            return False

# Define the root directory
root_directory = '.'  # Change this to the desired root directory if needed

# Define the phrase to search for
target_phrase = "0 (EX_OK: successful termination)"

# Output file to store the results
output_file = "sync_results.txt"

# List all files in the root directory
files = [f for f in os.listdir(root_directory) if os.path.isfile(os.path.join(root_directory, f))]

# Check each file for the specified phrase
with open(output_file, 'w') as output:
    for file_name in files:
        file_path = os.path.join(root_directory, file_name)
        if check_file(file_path, target_phrase):
            output.write(f"{file_name} = OK\n")
        else:
            output.write(f"{file_name} = not OK\n")

print(f"Sync results have been written to {output_file}")
