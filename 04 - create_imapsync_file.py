import pandas as pd

# Function to write data to a text file in the required format
def write_to_file(output_filename, data):
    with open(output_filename, 'a') as file:
        for line in data:
            file.write(';'.join(line) + ';\n')
        # Add an extra ';' at the end
        file.write(';;')

# Get domain name from user input
domain_name = input("Enter the domain name (e.g., example.com.br): ")

# Prepare filenames
input_file = f'address_importer_{domain_name}.xlsx'
output_filename = f'05_imapsync_{domain_name}.txt'

# Read the Excel file
df = pd.read_excel(input_file)

# Extract required columns from the Excel file
source_addresses = df['Email'].tolist()
source_passwords = df['Password'].tolist()

# Define fixed values
source_server = 'source_imap_server.example.com.br'
dest_server = 'dest_imap_server.example.com.br'

# Prepare the data to write into the file
data = []
for source_address, source_password in zip(source_addresses, source_passwords):
    data.append([source_server, source_address, source_password, dest_server, source_address, source_password])

# Write data to the output file
write_to_file(output_filename, data)

print(f"File '{output_filename}' has been created successfully.")
