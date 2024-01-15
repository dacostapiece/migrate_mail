import csv

def read_csv_file(domain_name):
    filename = f"address_importer_{domain_name}.csv"
    data = []
    with open(filename, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def write_to_csv_file(domain_name, data):
    fieldnames = ['IMAP user name', 'IMAP password', 'Email address (optional)', 'MailStore username (optional)']
    filename = f"address_importer_mailstore_{domain_name}.csv"
    with open(filename, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for row in data:
            row_data = {
                'IMAP user name': row.get('Email', ''),
                'IMAP password': row.get('Password', ''),
                'Email address (optional)': row.get('Email', ''),
                'MailStore username (optional)': ''
            }
            writer.writerow(row_data)

def main():
    domain_name = input("Enter domain name (ex. example.com.br): ")
    need_new_password = input("Need to set a new password? (yes/no): ").lower()
    
    data = read_csv_file(domain_name)
    
    if need_new_password == 'yes':
        new_password = input("Enter new password: ")
        for row in data:
            row['Password'] = new_password
            
    write_to_csv_file(domain_name, data)
    print(f"CSV file address_importer_mailstore_{domain_name}.csv generated successfully!")

if __name__ == "__main__":
    main()
