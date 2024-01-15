# migrate_mail
Scripts that will help you out on migrating emails (cPanel/WHM)

These scripts are here to help you migrating mail messages TO a server where YOU DON'T have root access.
This scenario requires both source and destination server is cPanel/WHM.

1) Go to source server, intended for migration cPanel account, E-mail, Email Accounts page, set page to list all mail accounts into a single page
2) Select all text within your browser and save content as input.txt - drag and drop this file to your "desire migration folder"
These python scripts were created and tested within Windows 10, they may work with Unix distributions (Ex.: Ubuntu), but i have not tested
If you are running on Windows 10 like me, please install python - here i'm using Python 3.11.2. You will also need to install pip and some other library to handle xlsx files. Paste errors on chatgpt as i did.
3) run "python 01 - filter_mail_from_page.py" from your "desire migration folder", the folder must have input.txt grabbed previously - over here i've opened cmd prompt and navigated to this folder like "cd c:\users\rafael\desire migration folder" then you call the python script
4) this script will output single_list_mail_addresses_example.com.br.txt which is basically a list of mail addresses pulled out from previous select all copy/paste.
5) run "python 02 - create_address_importer_file.py" from your "desire migration folder" - this script will grab single_list_mail_addresses_example.com.br.txt and create two files - a CSV and a XLSX file. XLSX file will be used in future scripts and CSV is going to be use in Address Importer funcionality in cPanel in order to create mail accounts, set passwords and quota disk for email account.
Please advise setting a password that suits password complexity in source/dest server.
Please advise setting a quota that will be suitable for most of email accounts, otherwise mail syncing will fail due to lack of space. You can manually adjust quota size on dest server after address importation
6) Access cpanel account on source server, go to file manager, import address_importer_example.com.br.xlsx and 03 - change_mail_passwords.py - these files will be available somewhere above public_html, here i created a imapsync folder to keep things organized 
On CentOS, operational system for cPanel/WHM - (Alma linux may be the same), it will have installed python 2 - in my case python 2.7.5, you can install a newer version python along current one.
You will also need to install pip and some other library to handle xlsx files. Paste errors on chatgpt as i did or ask to help to install a newer python install.
Here i installed python 3.6 on CentOS and i called this python version with "python3.6"
8) Access on the source server with terminal, you can access terminal on browser through WHM panel
9) Go to the folder where you imported address_importer_example.com.br.xlsx and 03 - change_mail_passwords.py - like cd /home/example/public_html/imapsync
10) run "python3.6 03 - change_mail_passwords.py" this script will grab mail addresses, passwords and cpanel account username in order to reset mail account passwords - so we can sync mail between servers with a list more easily
11) Go to dest server, create you cPanel account, let cPanel account username with domain name without ".com" / ".com.br" etc...
12) Access this cPanel account, go to Mail, Address importer and open file  address_importer_example.com.br.csv - go advancing until it finishes successful
13) Go back to "desire migration folder" and run "python 04 - create_imapsync_file.py" - this script will output 05_imapsync_example.com.br.txt - this file will be used along imapsync to sync mail between source and dest server
PLEASE UPDATE source_server and dest_server to YOUR CORRESPONDING Source and Dest Servers. Use IMAP addresses.
https://imapsync.lamiral.info/
I already used imapsync online and locally with single and individual mail accounts when syncing. I haven't tried syncing multiple accounts on Linux like Ubuntu this time, but with file  05_imapsync_example.com.br.txt and the corresponding script to sync multiple accounts, you will be fine
In my case, i runned imapsync on Windows 10. In Windows, you will place 05_imapsync_example.com.br.txt on the same folder as binary imapsync is along this sync_loop_windows.bat - in my case, i duplicate sync_loop_windows.bat so i could mess with it without losing original bat file
imapsync Windows binary is not openly available for users, but you'll research internet, you'll finally get its link, given my Gilles Lamiral itself, imapsync author. Please donate to his project if you can
15) Open new_sync_loop_windows.bat with a text editor and replace all "file.txt" with 05_imapsync_example.com.br.txt
16) Click twice on new_sync_loop_windows.bat to start the syncing job
17) Each synced mail account will output on console as well as save a log file like 2024_01_14_20_05_32_571_teste_example_com_br_teste_example_com_br.txt inside LOG_imapsync folder
18) After completion, you can open the corresponding mail account sync log file and look after in the bottom for this:
Exiting with return value 0 (EX_OK: successful termination) 0/50 nb_errors/max_errors PID 14788
if value 0 (EX_OK: successful termination) then you are alright.
19) You can use audit.py - this script will look all TXT files in its own directory and create a list of mail addresses along "not OK" or "OK" so you can review individual fails among several files.
You may update this code to output results in separate files for better review.
20) Before shutting down (cancel) source server, you may like to backup these mails somewhere else locally
I've asked chatgpt to create a python script what would get file  address_importer_example.com.br.csv created previously to achive this
run "python 08 - create_address_importer_mailstore_file.py" - it will output file  address_importer_mailstore_example.com.br.csv
21) Download Mailstore Server Trial version https://www.mailstore.com/en/products/mailstore-server/
22) Get your free trial license code on your email, do basic install, go to Archive Email, select E-mail Servers/Other Server via IMAP/POP3/Multiple Mailboxes (CSV File)/set source (or dest) imap mail server will want to backup, click accept all certificates - in csv file past full directory path along file address_importer_example.com.br.csv
Follow instructions, click em Finish and wait download
23) After itfinishes, go to Administrative Tools/Compliance/Compliance General/Archive Access - set tp allow access to administrators - so you can handle what it was backed up.
24) Backups will be shown under Other archives
25) You can export this info in Export E-mail/E-mail Files/Export to PST file/All folders (or individual one/Export Email to a new or existing pst file - set a new file  name and click finish - i'd like to export several individual  PSTs all at once, but i still dont how to do it. You can reach out Mailstore for this
