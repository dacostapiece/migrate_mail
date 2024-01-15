import openpyxl
import subprocess

def call_uapi(username, email, password):
    command = [
        'uapi',
        '--output=jsonpretty',
        f'--user={username}',
        'Email',
        'passwd_pop',
        f'email={email}',
        f'password={password}'
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    # Check for errors
    if stderr:
        print(f"Error: {stderr.decode('utf-8')}")

    return stdout.decode('utf-8')


def process_excel(domain):
    # Construct the filename based on the provided domain
    filename = f"address_importer_{domain}.xlsx"

    try:
        wb = openpyxl.load_workbook(filename)
        sheet = wb.active
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        return

    # Output file for API responses
    output_filename = f"api_{domain}_output.txt"
    output_file = open(output_filename, 'w')

    # Loop through rows and call UAPI for each email-password pair
    for row in sheet.iter_rows(min_row=2, values_only=True):  # Assuming data starts from row 2
        email, password, _ = row  # Assuming the third column is Quota and ignored

        # Call UAPI for each email-password pair
        result = call_uapi(username=domain.split('.')[0], email=email, password=password)
        output_file.write(f"{result}\n")  # Write API response to the output file

    output_file.close()
    print(f"API responses saved to '{output_filename}'.")

# Example usage
domain_name = input("Enter the domain name (e.g., snsec.com): ")
process_excel(domain_name)
