import pandas as pd

# Get domain name from user input
domain_name = input("Enter the domain name (e.g., example.com.br): ")

# Get default password from user input
default_password = input("Enter the default password: ")

# Get quota from user input
quota = int(input("Enter the quota (e.g., 100, 1000, 10000): "))

# Determine input file based on domain name
input_file = f'single_list_mail_addresses_{domain_name}.txt'

# Read email addresses from the input file
with open(input_file, 'r') as file:
    emails = [line.strip() for line in file]

# Create a DataFrame with columns Email, Password, and Quota
data = {
    'Email': emails,
    'Password': [default_password] * len(emails),
    'Quota': [quota] * len(emails)
}

df = pd.DataFrame(data)

# Save DataFrame to an Excel file (.xlsx)
output_file_xlsx = f'address_importer_{domain_name}.xlsx'
df.to_excel(output_file_xlsx, index=False, engine='openpyxl')
print(f"Spreadsheet '{output_file_xlsx}' has been created successfully.")

# Save DataFrame to CSV file (.csv)
output_file_csv = f'address_importer_{domain_name}.csv'
df.to_csv(output_file_csv, index=False)
print(f"CSV file '{output_file_csv}' has been created successfully.")
