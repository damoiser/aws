
import subprocess

print("THIS SCRIPT IS STILL IN WORK IN PROGRESS - DONT USE IT YET")

print("this script will delete all archives and the vault, see glacier/README.md for further details how it works")


account_id = input("enter account id (blank if same as configured in aws): ")
if account_id == "":
  # if using the default one use dash
  account_id = "-"


aws_vaults = subprocess.run(['aws', 'glacier', 'list-vaults', '--account-id', account_id], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n')


while True:
  vault_name = input("enter vault name: ")

  if vault_name == "":
    print("please define a valid vault name...")
  else:
    break


aws_region = subprocess.run(['aws', 'configure', 'get', 'region'], stdout=subprocess.PIPE).stdout.decode('utf-8').strip('\n')

region = input("enter region (blank for " + aws_region + "): ")

if region == "":
  region = aws_region


