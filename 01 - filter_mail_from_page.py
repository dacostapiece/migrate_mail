import re

# Function to extract email addresses from a given text and domain
def extract_emails(input_text, domain):
    email_pattern = rf'\b[A-Za-z0-9._%+-]+@{domain}\b'
    emails = re.findall(email_pattern, input_text)
    return emails

# Get the domain name from user input
domain = input("Enter the domain name (e.g., example.com.br): ")

# Read from input.txt and extract email addresses for the given domain
with open('input.txt', 'r') as input_file:
    input_text = input_file.read()
    emails = extract_emails(input_text, domain)

# Define the output file name including the domain name
output_file_name = f'single_list_mail_addresses_{domain}.txt'

# Write the extracted email addresses to the output file with the domain name
with open(output_file_name, 'w') as output_file:
    for email in emails:
        output_file.write(email + '\n')
